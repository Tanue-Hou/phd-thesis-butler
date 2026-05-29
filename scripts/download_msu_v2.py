#!/usr/bin/env python3
"""
MSU Dissertation Downloader - v2 with better timeout handling
Downloads full dissertations and avtoreferaty from dissovet.msu.ru
"""
import subprocess, json, re, os, time, sys, signal
from pathlib import Path

BASE = "/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler/data/MSU"
TIMEOUT_PAGE = 8   # seconds for page fetch
TIMEOUT_FILE = 15  # seconds for file download

def log(msg):
    print(f"[MSU] {msg}")
    sys.stdout.flush()

def safe_curl(url, timeout=TIMEOUT_PAGE):
    """Curl with timeout, returns (success, output)"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), url, 
             "--connect-timeout", "5", "--retry", "1", "--retry-delay", "1"],
            capture_output=True, text=True, timeout=timeout+5
        )
        return True, r.stdout
    except subprocess.TimeoutExpired:
        return False, ""
    except:
        return False, ""

def download_file(url, filepath):
    """Download with strict timeout"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(TIMEOUT_FILE), 
             "--connect-timeout", "5", url, "-o", str(filepath), "-w", "%{http_code}"],
            capture_output=True, text=True, timeout=TIMEOUT_FILE+5
        )
        if r.stdout.strip() == "200" and filepath.exists() and filepath.stat().st_size > 1000:
            return True
        if filepath.exists() and filepath.stat().st_size < 100:
            filepath.unlink(missing_ok=True)
    except:
        if filepath.exists():
            filepath.unlink(missing_ok=True)
    return False

# Fetch metadata
success, html = safe_curl("https://dissovet.msu.ru/api/dissertations", 20)
if not success:
    log("ERROR: failed to fetch API")
    sys.exit(1)

all_data = json.loads(html)
recent = [d for d in all_data 
          if d.get('announcedDate','')[:4].isdigit() 
          and 2023 <= int(d['announcedDate'][:4]) <= 2026]

log(f"Total: {len(recent)} dissertations (2023-2026)")

stats = {"downloaded": 0, "failed": 0, "skipped": 0}

for i, entry in enumerate(recent):
    code = entry.get('dissertationCode', '')
    fullname = entry.get('fullname', 'Unknown')
    subject = entry.get('industryName', 'Unknown')
    title = entry.get('title', '')
    year = entry.get('announcedDate', '')[:4]
    
    if not code:
        stats['skipped'] += 1
        continue
    
    # Build path
    author_folder = re.sub(r'[\\/*?:"<>|]', '_', fullname.replace(' ', '_'))
    subject_folder = subject.replace(' ', '_').replace('/', '_')
    dest_dir = Path(BASE) / subject_folder / author_folder
    
    # Skip if already complete
    diss_path = dest_dir / "диссертация.pdf"
    avtoref_path = dest_dir / "автореферат.pdf"
    
    if diss_path.exists() and diss_path.stat().st_size > 1000:
        stats['skipped'] += 1
        if (i+1) % 50 == 0:
            log(f"[{i+1}/{len(recent)}] {fullname[:30]}... (exists)")
        continue
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Get dissertation page
    success, page_html = safe_curl(f"https://dissovet.msu.ru/dissertation/{code}")
    if not success:
        stats['failed'] += 1
        continue
    
    # Extract file UUIDs
    file_uuids = re.findall(r'/file/dissovet-docs/([a-f0-9-]+)', page_html)
    if not file_uuids:
        stats['failed'] += 1
        continue
    
    # Get unique UUIDs and their sizes
    file_info = []
    for uuid in set(file_uuids):
        try:
            r = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "5", "--connect-timeout", "3",
                 f"https://dissovet.msu.ru/file/dissovet-docs/{uuid}",
                 "-o", "/dev/null", "-w", "%{http_code} %{size_download}"],
                capture_output=True, text=True, timeout=8
            )
            parts = r.stdout.strip().split()
            if len(parts) >= 2 and parts[0] == "200":
                file_info.append((uuid, int(parts[1])))
        except:
            pass
    
    if not file_info:
        stats['failed'] += 1
        continue
    
    # Sort by size: largest = dissertation, smallest = avtoreferat
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    # Download files
    dl_ok = False
    for idx, (uuid, fsize) in enumerate(file_info[:2]):
        file_url = f"https://dissovet.msu.ru/file/dissovet-docs/{uuid}"
        target = diss_path if idx == 0 else avtoref_path
        
        if not target.exists() or target.stat().st_size < 100:
            ok = download_file(file_url, target)
            if ok: dl_ok = True
    
    # Write meta
    meta = {
        "author": fullname, "title": title, "year": year,
        "source": "MSU", "source_url": f"https://dissovet.msu.ru/dissertation/{code}",
        "industry": subject, "files": {}
    }
    if diss_path.exists() and diss_path.stat().st_size > 1000:
        meta["files"]["dissertation"] = "диссертация.pdf"
    if avtoref_path.exists() and avtoref_path.stat().st_size > 1000:
        meta["files"]["avtoreferat"] = "автореферат.pdf"
    
    with open(dest_dir / "meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    if dl_ok:
        stats['downloaded'] += 1
    else:
        stats['failed'] += 1
    
    if (i+1) % 20 == 0:
        log(f"[{i+1}/{len(recent)}] {fullname[:30]}... "
            f"DL={stats['downloaded']} FAIL={stats['failed']} SKIP={stats['skipped']}")
    
    time.sleep(0.2)

log(f"\nDONE: {stats['downloaded']} DL, {stats['failed']} FAIL, {stats['skipped']} SKIP")
