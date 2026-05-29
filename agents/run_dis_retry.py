#!/usr/bin/env python3
"""
Phase 2 DIS Retry Runner — 重跑 637 个 dead_letter 论文
10 workers, 降低并发避免 API 限流
"""
import subprocess, json, os, sys, time, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
QUEUE = BASE / "queue"
TODO = QUEUE / "todo"
DOING = QUEUE / "doing"
DONE = QUEUE / "done"
DEAD = QUEUE / "dead_letter"
WORKER = str(BASE / "agents/worker.py")
NUM_WORKERS = 10

log_lock = threading.Lock()
t_start = time.time()

def report():
    elapsed = time.time() - t_start
    done_count = len(list(DONE.iterdir()))
    dead_count = len(list(DEAD.iterdir()))
    todo_count = len(list(TODO.iterdir()))
    doing_count = len(list(DOING.iterdir()))
    rate = done_count / (elapsed / 60) if elapsed > 0 else 0
    msg = f"[{elapsed/60:.0f}min] DIS-RETRY done={done_count} dead={dead_count} todo={todo_count} doing={doing_count} rate={rate:.1f}/min"
    print(msg)
    with log_lock:
        with open(BASE / "logs" / "dis_retry.log", "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def process_one(job_file):
    job_name = job_file.name
    doing_file = DOING / job_name
    try:
        os.rename(str(job_file), str(doing_file))
    except:
        return
    r = subprocess.run(
        ["python3", WORKER, "--job", str(doing_file), "--output", "data/raw"],
        capture_output=True, text=True, timeout=180
    )
    if r.returncode == 0:
        shutil.copy2(str(doing_file), str(DONE / job_name))
        doing_file.unlink()
    else:
        with open(doing_file) as f:
            job = json.load(f)
        job["retry"] = job.get("retry", 0) + 1
        if job["retry"] >= 3:
            shutil.copy2(str(doing_file), str(DEAD / job_name))
            doing_file.unlink()
        else:
            with open(str(TODO / job_name), 'w') as f:
                json.dump(job, f)
            doing_file.unlink()

print("PHASE 2 DIS RETRY — 637 jobs, 10 workers (low concurrency)")
print(f"Starting: todo={len(list(TODO.iterdir()))}")
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
        time.sleep(3)

for f in as_completed(all_futures):
    pass

elapsed = time.time() - t_start
done_count = len(list(DONE.iterdir()))
dead_count = len(list(DEAD.iterdir()))
print(f"\nDIS RETRY COMPLETE")
print(f"  FINAL: done={done_count} dead={dead_count} time={elapsed:.0f}s")
