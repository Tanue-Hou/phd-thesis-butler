"""Metadata-only retrieval from the public writing-knowledge projection."""
from contextlib import closing
from pathlib import Path
import secrets
import sqlite3
import time

from editorial import GLOSSARY, guidance
from policy import OUTPUTS, SCENES, TYPES, WRITING_MOVES

MOVES = {
    **WRITING_MOVES,
    "no_significant_difference": "报告未确认显著差异",
    "test_whether": "表述待检验问题",
    "report_observation": "报告给定条件下的观察",
}
PAGE_SIZE = 3
TASK_LIMIT = 12
KEY_LIMIT = 24
TASK_TTL = 1800
KEY_WINDOW = 86400


def route_kinds(database: Path):
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        marks = ",".join("?" for _ in SCENES)
        return tuple(row[0] for row in db.execute(
            f"SELECT DISTINCT kind FROM scene_route WHERE scenario IN ({marks}) "
            "AND kind IS NOT NULL ORDER BY kind", SCENES
        ))


class SceneCards:
    def __init__(self, gateway, kinds):
        self.gateway = gateway
        self.kinds = kinds
        self.tasks = {}
        self.released = {}

    def lookup(self, request):
        now = time.monotonic()
        request_id = secrets.token_hex(8)
        query_count = 0

        def result(decision, reason, cards=None, handle=None, more=False):
            return dict(request_id=request_id, decision=decision, reason_code=reason,
                        db_query_count=query_count, cards=cards or [], task_handle=handle,
                        has_more=more)

        if not self.gateway.reserve_call(now):
            return result("deny", "LIMIT")
        if not isinstance(request, dict) or set(request) - {
            "intent", "scene", "kind", "writing_move", "task_handle"
        }:
            return result("deny", "INVALID_REQUEST")
        enums = {"intent": tuple(OUTPUTS), "scene": SCENES,
                 "kind": self.kinds, "writing_move": tuple(MOVES)}
        for field, choices in enums.items():
            if field in request or field in ("intent", "scene"):
                value = request.get(field)
                if type(value) is not str or value not in choices:
                    return result("deny", "INVALID_REQUEST")

        self.tasks = {handle: state for handle, state in self.tasks.items()
                      if now - state[0] < TASK_TTL}
        if "task_handle" in request:
            handle = request["task_handle"]
            if type(handle) is not str or len(handle) != 32 or handle not in self.tasks:
                return result("clarify", "TASK_EXPIRED")
        else:
            if len(self.tasks) >= 1000:
                return result("deny", "LIMIT")
            handle = secrets.token_urlsafe(24)
        seen = self.tasks.get(handle, (now, set()))[1]
        if len(seen) >= TASK_LIMIT:
            return result("deny", "LIMIT", handle=handle)
        self.released = {card: stamp for card, stamp in self.released.items()
                         if now - stamp < KEY_WINDOW}

        where = ["scenario=?"]
        args = [request["scene"]]
        if "kind" in request:
            where.append("kind=?")
            args.append(request["kind"])
        if "writing_move" in request:
            where.append("move=?")
            args.append(MOVES[request["writing_move"]])
        try:
            uri = self.gateway.database.resolve().as_uri() + "?mode=ro"
            with closing(sqlite3.connect(uri, uri=True)) as db:
                db.row_factory = sqlite3.Row
                query_count = 1
                rows = db.execute(
                    "SELECT stage, knowledge_id, kind, move, requirements, misuse, evidence_basis, "
                    "independent_support, template, grammar FROM scene_route WHERE "
                    + " AND ".join(where) + " ORDER BY stage, knowledge_id, kind", args
                ).fetchall()
        except sqlite3.Error:
            return result("error", "UNAVAILABLE")

        preferred = TYPES[request["intent"]]
        rows.sort(key=lambda row: row["kind"] not in preferred)
        cards = []
        emitted = set(seen)
        release_slots = KEY_LIMIT - len(self.released)
        hit_key_limit = False
        more = False
        for row in rows:
            card_id = row["knowledge_id"]
            if card_id in emitted:
                continue
            if card_id not in self.released and release_slots == 0:
                hit_key_limit = True
                continue
            if len(cards) == min(PAGE_SIZE, TASK_LIMIT - len(seen)):
                more = len(emitted) < TASK_LIMIT
                break
            if card_id not in self.released:
                self.released[card_id] = now
                release_slots -= 1
            emitted.add(card_id)
            cards.append(dict(row))
        self.tasks[handle] = (now, emitted)
        if cards:
            reply = result("allow", "ALLOW", cards, handle, more)
            if request["intent"] in ("translate", "polish"):
                reply["glossary_guidance"] = GLOSSARY
            if request["intent"] == "polish":
                reply["editorial_guidance"] = guidance()
            return reply
        if hit_key_limit:
            return result("deny", "LIMIT", handle=handle)
        return result("no_match", "NO_MATCH", handle=handle)
