"""Operator CLI for the PTB access registry and audit ledger (stdlib only)."""
import argparse
import csv
import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

def connect(path, mode):
    return sqlite3.connect(Path(path).resolve().as_uri() + "?mode=" + mode, uri=True)

def initialize(registry, manifest):
    rows = list(csv.DictReader(Path(manifest).read_text("utf-8-sig").splitlines()))
    if len(rows) != 200 or len({r["id"] for r in rows}) != 200:
        raise ValueError("Expected 200 unique slots")
    for r in rows:
        if len(bytes.fromhex(r["digest"])) != 32:
            raise ValueError("Bad SHA-256")
    with closing(connect(registry, "rwc")) as db, db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("""CREATE TABLE keys(id TEXT PRIMARY KEY, digest TEXT UNIQUE NOT NULL,
                   owner TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 0)""")
        db.executemany("INSERT INTO keys(id,digest) VALUES (:id,:digest)",rows)

def identify(registry, header):
    if not header:
        return "", "", "missing_key"
    scheme, _, key = header.partition(b" ")
    if scheme.lower() != b"bearer" or len(key) != 12:
        return "", "", "invalid_key"
    with closing(connect(registry,"ro")) as db:
        row = db.execute("SELECT id,owner,active FROM keys WHERE digest=?",
                         (hashlib.sha256(key).hexdigest(),)).fetchone()
    if not row:
        return "", "", "invalid_key"
    slot, owner, active = row
    return slot, owner, ("ok" if active and owner else "inactive_key")

def init_events(path):
    with closing(connect(path,"rwc")) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS events(ts TEXT DEFAULT
            (strftime('%Y-%m-%dT%H:%M:%fZ','now')), slot TEXT, owner TEXT,
            action TEXT, decision TEXT, reason TEXT, request_id TEXT, queries INTEGER, cards INTEGER)""")

def record(path, identity, action, decision, reason, request_id="", queries=0, cards=0):
    with closing(connect(path,"rw")) as db, db:
        db.execute("INSERT INTO events(slot,owner,action,decision,reason,request_id,queries,cards) VALUES (?,?,?,?,?,?,?,?)",
                   (*identity[:2],action,decision,reason,request_id,queries,cards))

def manage():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", default="/opt/ptb-beta/access/keys.sqlite")
    p.add_argument("--events", default="/opt/ptb-beta/audit/events.sqlite")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("init").add_argument("manifest")
    for action in ("bind","revoke"):
        cmd=sub.add_parser(action)
        cmd.add_argument("slot")
        if action=="bind":
            cmd.add_argument("owner")
    sub.add_parser("list")
    sub.add_parser("usage")
    args=p.parse_args()
    if args.command=="init":
        return initialize(args.registry,args.manifest)
    if args.command=="usage":
        with closing(connect(args.events,"ro")) as db:
            for row in db.execute("""SELECT slot,owner,action,decision,reason,count(*),sum(queries),sum(cards)
                                     FROM events GROUP BY slot,owner,action,decision,reason ORDER BY slot,owner"""):
                print(*row,sep="\t")
        return
    with closing(connect(args.registry,"ro" if args.command=="list" else "rw")) as db, db:
        if args.command=="list":
            for row in db.execute("SELECT id,owner,active FROM keys ORDER BY id"):
                print(*row,sep="\t")
        else:
            if args.command=="bind":
                owner=args.owner.strip()
                if not owner or len(owner)>120 or not owner.isprintable():
                    p.error("Use a printable user label of 1-120 characters")
                cursor=db.execute("UPDATE keys SET owner=?,active=1 WHERE id=?",(owner,args.slot))
            else:
                cursor=db.execute("UPDATE keys SET active=0 WHERE id=?",(args.slot,))
            if cursor.rowcount!=1:
                p.error("Unknown slot")

if __name__=="__main__":
    manage()
