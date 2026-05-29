#!/usr/bin/env python3
"""
Phase 2 Pilot Runner — 8 parallel workers, 30 jobs
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
OUTPUT_DIR = str(BASE / "data/raw")

log_lock = threading.Lock()
stats = {"ok": 0, "fail": 0, "dead": 0, "total": 0}

def process_one(job_file):
    job_name = job_file.name
    doing_file = DOING / job_name
    try:
        os.rename(str(job_file), str(doing_file))
    except:
        return

    with log_lock:
        stats["total"] += 1

    t0 = time.time()
    r = subprocess.run(
        ["python3", WORKER, "--job", str(doing_file), "--output", "data/raw"],
        capture_output=True, text=True, timeout=180
    )
    elapsed = time.time() - t0

    if r.returncode == 0:
        shutil.copy2(str(doing_file), str(DONE / job_name))
        doing_file.unlink()
        with log_lock:
            stats["ok"] += 1
        print(f"  [+] {job_name} | {elapsed:.0f}s | {r.stdout.strip()[:80]}")
    else:
        with open(doing_file) as f:
            job = json.load(f)
        job["retry"] = job.get("retry", 0) + 1

        if job["retry"] >= 3:
            shutil.copy2(str(doing_file), str(DEAD / job_name))
            doing_file.unlink()
            with log_lock:
                stats["dead"] += 1
            print(f"  [X] {job_name} | DEAD | {r.stderr[:80]}")
        else:
            with open(str(TODO / job_name), 'w') as f:
                json.dump(job, f)
            doing_file.unlink()
            with log_lock:
                stats["fail"] += 1
            print(f"  [R] {job_name} | retry {job['retry']}")

print("=" * 60)
print("PHASE 2 PILOT — 30 jobs, 8 workers")
print("=" * 60)

t_start = time.time()

with ThreadPoolExecutor(max_workers=8) as ex:
    all_futures = []
    for _ in range(3):  # Feed rounds
        jobs = list(TODO.iterdir())
        for jf in jobs:
            all_futures.append(ex.submit(process_one, jf))
        time.sleep(3)

    for f in as_completed(all_futures):
        pass

    # Handle retries
    remaining = list(TODO.iterdir())
    if remaining:
        more = []
        for jf in remaining:
            more.append(ex.submit(process_one, jf))
        for f in as_completed(more):
            pass

t_total = time.time() - t_start

print(f"\n{'='*60}")
print(f"RESULTS")
print(f"{'='*60}")
print(f"  OK:   {stats['ok']}")
print(f"  FAIL: {stats['fail']}")
print(f"  DEAD: {stats['dead']}")
print(f"  Time: {t_total:.0f}s")

# G1 verification
raw_dirs = [d for d in (BASE / "data/raw").iterdir() if d.is_dir()]
print(f"\nG1 Gate on raw outputs:")
total_tmpl = 0
total_files = 0
g1_ok = True
for d in raw_dirs:
    files = list(d.glob("*.jsonl"))
    total_files += len(files)
    for f in files:
        with open(f) as fh:
            for line in fh:
                e = json.loads(line)
                total_tmpl += 1
                # G1 checks
                if "___" in e.get("template", ""):
                    print(f"  ❌ ___ found in {f.name}")
                    g1_ok = False
                if not e.get("category") or not e.get("subtype"):
                    print(f"  ❌ Missing fields in {f.name}")
                    g1_ok = False

print(f"  Files: {total_files}")
print(f"  Templates: {total_tmpl}")
print(f"  G1 Gate: {'✅ PASS' if g1_ok else '❌ FAIL'}")
