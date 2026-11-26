"""Build the fictional PTB test fixture in a new file."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

DEMO_ID = 0x50544244
ROWS = (
    ("篇章布局", "整篇布局", "设计纸飞机观察记录的结构", "说明观察问题后列出记录步骤。", ""),
    ("边界与归属", "俄语句式", "区分自述和他人观察", "保留观察者。", "По наблюдениям [кого], [что произошло]."),
    ("结果与不确定性", "俄语语用", "保留不确定性", "作者原稿含有可能性限定。", "Возможно, [наблюдение]."),
    ("实验验证", "对照证据", "对比两架虚构纸飞机的试飞", "记录相同投放条件。", ""),
)

def build(path):
    with path.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(path)) as db, db:
            db.execute(f"PRAGMA application_id={DEMO_ID}")
            db.execute("""CREATE TABLE scene_route (scenario TEXT, stage INTEGER, knowledge_id TEXT,
                kind TEXT, move TEXT, requirements TEXT, misuse TEXT, evidence_basis TEXT,
                independent_support INTEGER, template TEXT, grammar TEXT)""")
            for i, (tag, kind, move, requirement, template) in enumerate(ROWS, 1):
                db.execute("INSERT INTO scene_route VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                           (tag, i, f"demo-{i}", kind, move, requirement, "仅用于虚构演示",
                            "fictional", 0, template, ""))
    except Exception:
        path.unlink()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
