#!/usr/bin/env python3
"""
Phase 2 AREF Runner — 全量抽取 MSU автореферат
587 jobs, 20 parallel workers
"""
import subprocess, json, os, sys, time, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
QUEUE = BASE / "queue"
TODO = QUEUE / "aref_todo"
DOING = QUEUE / "aref_doing"
DONE = QUEUE / "aref_done"
DEAD = QUEUE / "aref_dead"
WORKER = str(BASE / "agents/aref_worker.py")
NUM_WORKERS = 15

log_lock = threading.Lock()
stats = {"ok": 0, "fail": 0, "dead": 0}
t_start = time.time()

def report():
    elapsed = time.time() - t_start
    done_count = len(list(DONE.iterdir()))
    dead_count = len(list(DEAD.iterdir()))
    todo_count = len(list(TODO.iterdir()))
    doing_count = len(list(DOING.iterdir()))
    rate = done_count / (elapsed / 60) if elapsed > 0 else 0
    msg = f"[{elapsed/60:.0f}min] AREF done={done_count} dead={dead_count} todo={todo_count} doing={doing_count} rate={rate:.1f}/min"
    print(msg)
    with log_lock:
        with open(BASE / "logs" / "aref_run.log", "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def process_one(job_file):
    job_name = job_file.name
    doing_file = DOING / job_name
    try:
        os.rename(str(job_file), str(doing_file))
    except:
        return

    r = subprocess.run(
        ["python3", WORKER, "--job", str(doing_file), "--output", "data/raw/AREF"],
        capture_output=True, text=True, timeout=180
    )

    if r.returncode == 0:
        shutil.copy2(str(doing_file), str(DONE / job_name))
        doing_file.unlink()
        with log_lock:
            stats["ok"] += 1
    else:
        with open(doing_file) as f:
            job = json.load(f)
        job["retry"] = job.get("retry", 0) + 1
        if job["retry"] >= 3:
            shutil.copy2(str(doing_file), str(DEAD / job_name))
            doing_file.unlink()
            with log_lock:
                stats["dead"] += 1
        else:
            with open(str(TODO / job_name), 'w') as f:
                json.dump(job, f)
            doing_file.unlink()

print("PHASE 2 AREF RUN — 587 MSU автореферат, 20 workers")
print("=" * 60)
t_start = time.time()
last_report = time.time()
report_interval = 60

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as ex:
    all_futures = []
    while True:
        jobs = list(TODO.iterdir())
        if not jobs:
            if not list(DOING.iterdir()):
                break
            time.sleep(5)
            continue
        for jf in jobs:
            all_futures.append(ex.submit(process_one, jf))
        now = time.time()
        if now - last_report > report_interval:
            report()
            last_report = now
        time.sleep(2)

for f in as_completed(all_futures):
    pass

elapsed = time.time() - t_start
done_count = len(list(DONE.iterdir()))
dead_count = len(list(DEAD.iterdir()))
report()
print(f"\n{'='*60}")
print(f"AREF RUN COMPLETE")
print(f"{'='*60}")
print(f"  DONE: {done_count}")
print(f"  DEAD: {dead_count}")
print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f}min)")
