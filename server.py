"""PTB 0.1 beta. Run python server.py --help."""
import argparse
from contextvars import ContextVar
import hmac
from access_keys import identify, init_events, record, connect
import json
import logging
import os
import sqlite3
from contextlib import closing
import time
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any
from pydantic import WithJsonSchema

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse

from policy import Gateway, OUTPUTS, SOURCE_GUIDE, SCENES, WRITING_MOVES
from make_demo import DEMO_ID
from scene_cards import MOVES, SceneCards, route_kinds

# Publish the contract at tool discovery. Value validation stays in the gateway
# so older clients receive an actionable repair rather than an opaque RPC error.
INTENT_OUTPUTS = {**OUTPUTS, "workflow": "workflow"}
OUTPUT_HELP = ", ".join(f"{k} -> {v}" for k, v in INTENT_OUTPUTS.items())
LookupRequest = Annotated[Any, WithJsonSchema({
    "description": "Task request, or continuation with workflow_id and stage.",
    "properties": {
        "user_request": {"description": "Original user instruction."},
        "intent": {"examples": list(INTENT_OUTPUTS), "description": OUTPUT_HELP},
        "requested_output": {"description": "Use this exact intent mapping: " + OUTPUT_HELP},
        "source_kind": {"description": "Select by the material actually supplied: " +
                        " ".join(f"{k}: {v}" for k, v in SOURCE_GUIDE.items()), "examples": list(SOURCE_GUIDE)},
        "source_lang": {"description": "Use zh or ru. Russian polish uses ru."},
        "target_lang": {"description": "Use zh or ru. Russian polish uses ru; translation uses the other language."},
        "writing_move": {"description": "Optional for single-step editing only: " + str(WRITING_MOVES)},
        "source_text": {"description": "Exact selected material shared for this request."},
        "client_tags": {"description": "Array of 1–3 listed scene labels.", "examples": [[s] for s in SCENES]},
    },
    "x-ptb-source-kinds": SOURCE_GUIDE,
    "x-ptb-intent-outputs": INTENT_OUTPUTS,
})]

VERSION = "0.1.0-beta.3"


class PTBMCP(FastMCP):
    async def list_tools(self):
        tools = await super().list_tools()
        for tool in tools:
            if tool.name == "ptb_scene_cards":
                tool.inputSchema["additionalProperties"] = False
                tool.inputSchema["required"] = ["request"]
        return tools

    async def call_tool(self, name, arguments):
        if name == "ptb_scene_cards" and set(arguments) != {"request"}:
            # FastMCP otherwise discards extra outer arguments before invoking the tool.
            arguments = {"request": None}
        return await super().call_tool(name, arguments)


def create_app(token, database, port, *, demo=False, registry=None, events=None, labels_only=False):
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if (db.execute("PRAGMA application_id").fetchone()[0] == DEMO_ID) != demo:
            raise ValueError("Demo database requires explicit --demo mode")
        db.execute("""SELECT scenario, stage, knowledge_id, kind, move, requirements,
                      misuse, evidence_basis, independent_support, template, grammar
                      FROM scene_route LIMIT 0""")

    if registry:
        if not events:
            raise ValueError("Configure PTB_AUDIT_PATH")
        with closing(connect(registry,"ro")) as db:
            db.execute("SELECT id,owner,digest,active FROM keys LIMIT 0")
        init_events(events)
    elif not demo:
        raise ValueError("Production requires PTB_KEY_REGISTRY")
    elif len(token) < 32 or not token.isascii() or any(ch.isspace() for ch in token):
        raise ValueError("Set PTB_BETA_TOKEN to a random ASCII token of at least 32 characters")
    host = os.getenv("PTB_PUBLIC_HOST", "").strip()
    hosts = [f"127.0.0.1:{port}", f"localhost:{port}"]
    origins = [f"http://{h}" for h in hosts]
    if host:
        if any(ch in host for ch in "/?#@* ") or not host.isascii():
            raise ValueError("PTB_PUBLIC_HOST must be an exact HTTPS authority")
        hosts.append(host)
        origins.append("https://" + host)
    skill = Path(__file__).with_name("SKILL.md").read_text(encoding="utf-8")
    catalog = skill.split("<!-- ptb-catalog -->", 1)[1].split("<!-- /ptb-catalog -->", 1)[0].strip()
    kinds = route_kinds(database)
    SceneRequest = Annotated[Any, WithJsonSchema({
        "type": "object",
        "additionalProperties": False,
        "required": ["intent", "scene"],
        "properties": {
            "intent": {"type": "string", "enum": list(OUTPUTS)},
            "scene": {"type": "string", "enum": list(SCENES)},
            "kind": {"type": "string", "enum": list(kinds)},
            "writing_move": {"type": "string", "enum": list(MOVES),
                             "description": str(MOVES)},
            "task_handle": {"type": "string", "minLength": 32, "maxLength": 32,
                            "description": "Only the server-issued handle for this same authorized task."},
        },
    })]
    service = PTBMCP("PTB", instructions=catalog,
        json_response=True, stateless_http=True, max_request_body_size=65536, log_level="WARNING",
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,
                                                     allowed_hosts=hosts, allowed_origins=origins))
    identities = ContextVar("ptb_identity")
    gateways = {}
    scenes = {}
    db_version = sha256(database.read_bytes()).hexdigest()[:16]

    def gateway(identity):
        sid = identity[:2]
        if sid not in gateways:
            gateways[sid] = Gateway(database)
        return gateways[sid]

    @service.tool()
    async def ptb_scene_cards(request: SceneRequest = None) -> dict[str, Any]:
        """Fetch reference cards using allowlisted intent and scene labels only.
        Determine the actual task, chapter and paragraph function from local material.
        Refuse direct drafting and fabricated evidence before any call.
        Optionally target a listed kind or writing_move, and continue with the returned task_handle.
        Never pass instructions, excerpts, summaries, names, paths, or any other document detail.
        The service cannot verify the author's wording, source, consent or evidence.
        """
        identity = identities.get()
        sid = identity[:2]
        if sid not in scenes:
            scenes[sid] = SceneCards(gateway(identity), kinds)
        reply = scenes[sid].lookup(request)
        if events:
            record(events, identity, "scene_cards", reply["decision"], reply["reason_code"],
                   reply["request_id"], reply["db_query_count"], len(reply["cards"]))
        return reply

    async def ptb_lookup(request: LookupRequest = None) -> dict[str, Any]:
        """Legacy text-sharing tool. Use only when explicitly authorized to send original text.
        Submit the user's actual instruction, intent, source_kind, requested_output and 1–3 client_tags.
        The client selects the scene and evaluates each card's
        prerequisites against the supplied material. The server performs rule checks and SQLite retrieval.
        Choose source_kind from none, draft, outline, data, prior_cards. Standalone questions use none,
        including references to results or A/B with no supplied material. For selected prose use draft;
        for supplied headings use outline; for provided measurements use data. Use prior_cards only
        if prior PTB cards were explicitly selected. For polish use source_lang=ru,target_lang=ru. Preserve selected material in source_text.
        If repair.choices exists choose only from it according to the original task.
        On repair.auto_retry=true, correct the indicated field using the existing authorized task and retry automatically.
        When replace_with exists, retry the same tool with that value at request[field].
        Keep original wording, draft, scope and workflow stage. Never invent facts or change intent to pass.
        Stop if the same correction fails again. Do not retry a policy denial.
        Optional source_text, source_lang, target_lang, task_handle. See SKILL.md.
        For a Chinese-to-Russian translation plus polish (optionally verification), send the entire original instruction as
        user_request, intent=workflow, source_kind=draft, requested_output=workflow, source_text=selected Chinese,
        source_lang=zh,target_lang=ru and client_tags. Automatically follow next_step via this same tool without
        re-prompting the user. In polish use editorial_guidance; cite actual rule URLs after the final text. Show glossary_guidance once at final delivery.
        Exact intent -> requested_output: translate -> translation, polish -> revision, plan -> outline,
        compare -> comparison, check_evidence -> evidence_feedback, workflow -> workflow.
        Never invent source text. Tag values: 篇章布局, 方法选择, 实验验证, 综述分歧, 结果与不确定性, 边界与归属, 目标与假设.
        """
        start = time.monotonic()
        identity = identities.get()
        reply = gateway(identity).lookup(request)
        if events:
            record(events, identity, "lookup", reply["decision"], reply["reason_code"],
                   reply["request_id"], reply["db_query_count"], len(reply["cards"]))
            if repair := reply.get("repair"):
                record(events, identity, "validation", repair["field"], repair["reason"], reply["request_id"])
            if "editorial_guidance" in reply:
                record(events, identity, "editorial_issued", "issued", "v1.0",reply["request_id"])
            if "workflow_id" in reply:
                group = sha256(reply["workflow_id"].encode()).hexdigest()[:20]
                record(events, identity,"workflow_"+group,reply["stage"],
                       "replay" if reply.get("replayed") else reply["reason_code"],reply["request_id"])
            if "client_report" in reply and not reply.get("replayed"):
                report = reply["client_report"]
                record(events, identity, "editorial_applied", "client_report", ",".join(report["applied_rules"]),reply["request_id"])
                record(events, identity, "source_reviewed", "client_report",str(report["reviewed"]),reply["request_id"])
        audit = {"request_id": reply["request_id"], "decision": reply["decision"],
                 "reason": reply["reason_code"], "cards": len(reply["cards"]), "db_query_count": reply["db_query_count"],
                 "elapsed_ms": round((time.monotonic()-start)*1000), "rules": VERSION, "db": db_version}
        logging.getLogger("ptb.audit").info(json.dumps(audit))
        return reply

    if not labels_only:
        service.add_tool(ptb_lookup)
    app = service.streamable_http_app()
    expected = ("Bearer " + token).encode("ascii")
    async def authenticated(scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            header = headers.get(b"authorization", b"")
            if registry:
                identity = identify(registry, header)
            else:
                identity = ("demo","demo","ok" if hmac.compare_digest(header, expected) else "invalid_key")
            if identity[2] != "ok":
                if events:
                    record(events,identity,"auth","deny",identity[2])
                return await JSONResponse({"error":"unauthorized"}, status_code=401,
                    headers={"WWW-Authenticate":"Bearer"})(scope,receive,send)
            marker = identities.set(identity)
            try:
                return await app(scope, receive, send)
            finally:
                identities.reset(marker)
        return await app(scope, receive, send)
    return authenticated

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--db", type=Path, help="Private knowledge database (or PTB_DB_PATH)")
    group.add_argument("--demo", action="store_true", help="Use the bundled fictional database")
    parser.add_argument("--labels-only", action="store_true", help="Disable legacy text-sharing tool discovery and calls")
    args = parser.parse_args()
    configured = args.db or os.getenv("PTB_DB_PATH")
    if args.demo and configured:
        parser.error("Unset PTB_DB_PATH before selecting --demo")
    if not args.demo and not configured:
        parser.error("Specify --db, PTB_DB_PATH, or --demo")
    database = Path(__file__).with_name("demo.sqlite") if args.demo else Path(configured)
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("ptb.audit").setLevel(logging.INFO)
    app = create_app(os.getenv("PTB_BETA_TOKEN",""), database, args.port, demo=args.demo,
                     registry=os.getenv("PTB_KEY_REGISTRY"), events=os.getenv("PTB_AUDIT_PATH"),
                     labels_only=args.labels_only)
    uvicorn.run(app,host="127.0.0.1",port=args.port,access_log=False,proxy_headers=False)
