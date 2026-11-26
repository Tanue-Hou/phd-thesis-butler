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
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse

from policy import Gateway
from make_demo import DEMO_ID

VERSION = "0.1.0-beta.1"

def create_app(token, database, port, *, demo=False, registry=None, events=None):
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
    service = FastMCP("PTB", instructions="Use only after disclosure and approval of sending the request and selected draft. This service returns writing knowledge cards.",
        json_response=True, stateless_http=True, max_request_body_size=65536, log_level="WARNING",
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,
                                                     allowed_hosts=hosts, allowed_origins=origins))
    identities = ContextVar("ptb_identity")
    gateways = {}
    db_version = sha256(database.read_bytes()).hexdigest()[:16]
    @service.tool()
    async def ptb_lookup(request: dict[str, Any] | None = None) -> dict[str, Any]:
        """Submit the user's actual instruction, intent, source_kind, requested_output and 1–3 client_tags.
        Optional source_text, source_lang, target_lang, task_handle. See SKILL.md.
        Allowed intents: translate, polish, plan, compare, check_evidence.
        Never invent source text. Tag values: 篇章布局, 方法选择, 实验验证, 综述分歧, 结果与不确定性, 边界与归属, 目标与假设.
        """
        start = time.monotonic()
        identity = identities.get()
        # Binding changes start a separate task and rate-limit scope.
        sid = identity[:2]
        if sid not in gateways:
            gateways[sid] = Gateway(database)
        reply = gateways[sid].lookup(request)
        if events:
            record(events, identity, "lookup", reply["decision"], reply["reason_code"],
                   reply["request_id"], reply["db_query_count"], len(reply["cards"]))
        audit = {"request_id": reply["request_id"], "decision": reply["decision"],
                 "reason": reply["reason_code"], "cards": len(reply["cards"]), "db_query_count": reply["db_query_count"],
                 "elapsed_ms": round((time.monotonic()-start)*1000), "rules": VERSION, "db": db_version}
        logging.getLogger("ptb.audit").info(json.dumps(audit))
        return reply

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
                     registry=os.getenv("PTB_KEY_REGISTRY"), events=os.getenv("PTB_AUDIT_PATH"))
    uvicorn.run(app,host="127.0.0.1",port=args.port,access_log=False,proxy_headers=False)
