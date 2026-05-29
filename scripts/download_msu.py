#!/usr/bin/env python3
"""
MSU Dissertation Downloader
Downloads full dissertations and avtoreferaty from dissovet.msu.ru
Organizes by: data/MSU/{subject}/{author}/
"""

import subprocess, json, re, os, time, sys
from pathlib import Path

BASE = "/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler/data/MSU"

def log(msg):
    print(f"[MSU] {msg}")
    sys.stdout.flush()

def sanitize_filename(name):
    """Replace problematic chars for folder names"""
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

def get_author_folder(fullname):
    """Convert full name to folder name: Иванов Иван Петрович"""
    return sanitize_filename(fullname.replace(' ', '_'))

def get_subject_folder(industry_name):
    """Convert industry name to folder name"""
    return industry_name.replace(' ', '_').replace('/', '_')

def download_file(url, filepath, max_retries=3):
    """Download a file with retries"""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "30", url, "-o", filepath, "-w", "%{http_code}"],
                capture_output=True, text=True, timeout=35
            )
            if result.stdout == "200":
                size = os.path.getsize(filepath)
                if size > 1000:  # At least 1KB
                    return True, size
            # Remove empty/failed files
            if os.path.exists(filepath) and os.path.getsize(filepath) < 100:
                os.remove(filepath)
        except:
            pass
        if attempt < max_retries - 1:
            time.sleep(2)
    return False, 0

def get_dissertation_files(dissertation_code):
    """Get file UUIDs from a dissertation page"""
    url = f"https://dissovet.msu.ru/dissertation/{dissertation_code}"
    try:
        result = subprocess.run(["curl", "-s", "-L", "--max-time", "12", url],
                              capture_output=True, text=True, timeout=15)
        html = result.stdout
        
        # Find all file UUIDs
        file_links = re.findall(r'/file/dissovet-docs/([a-f0-9-]+)', html)
        
        # Determine which is dissertation vs avtoreferat by page context
        # The first PDF link is usually the dissertation
        # We look for indication in the surrounding text
        files = []
        for uuid in file_links:
            # Check file size/type
            check = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "8", 
                 f"https://dissovet.msu.ru/file/dissovet-docs/{uuid}",
                 "-o", "/dev/null", "-w", "%{http_code} %{size_download}"],
                capture_output=True, text=True, timeout=10
            )
            parts = check.stdout.split()
            if len(parts) >= 2 and parts[0] == "200":
                size = int(parts[1])
                files.append((uuid, size))
        
        return files
    except:
        return []

# Step 1: Fetch metadata API
log("Fetching MSU dissertation metadata...")
result = subprocess.run(["curl", "-s", "-L", "--max-time", "20", "https://dissovet.msu.ru/api/dissertations"],
                       capture_output=True, text=True, timeout=25)
all_data = json.loads(result.stdout)
log(f"Total in DB: {len(all_data)}")

# Step 2: Filter by year
recent = [d for d in all_data 
          if d.get('announcedDate','')[:4].isdigit() 
          and 2023 <= int(d['announcedDate'][:4]) <= 2026]
log(f"Last 3 years (2023-2026): {len(recent)} dissertations")

# Step 3: Process each dissertation
stats = {"downloaded": 0, "failed": 0, "skipped": 0, "total": len(recent)}

for i, entry in enumerate(recent):
    code = entry.get('dissertationCode', '')
    fullname = entry.get('fullname', 'Unknown')
    subject = entry.get('industryName', 'Unknown')
    title = entry.get('title', '')
    year = entry.get('announcedDate', '')[:4]
    
    if not code:
        stats['skipped'] += 1
        continue
    
    author_folder = get_author_folder(fullname)
    subject_folder = get_subject_folder(subject)
    
    dest_dir = Path(BASE) / subject_folder / author_folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    diss_path = dest_dir / "диссертация.pdf"
    avtoref_path = dest_dir / "автореферат.pdf"
    
    if diss_path.exists() and avtoref_path.exists() and diss_path.stat().st_size > 1000:
        stats['skipped'] += 1
        if (i+1) % 50 == 0:
            log(f"  [{i+1}/{len(recent)}] {fullname[:30]}... (already exists)")
        continue
    
    # Get files from dissertation page
    files = get_dissertation_files(code)
    
    if not files:
        stats['failed'] += 1
        if (i+1) % 50 == 0:
            log(f"  [{i+1}/{len(recent)}] {fullname[:30]}... no files found")
        continue
    
    # Download files - sort by size (larger = dissertation, smaller = avtoreferat)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Try to download
    downloaded = False
    for idx, (uuid, fsize) in enumerate(files[:2]):  # max 2 files per dissertation
        file_url = f"https://dissovet.msu.ru/file/dissovet-docs/{uuid}"
        if idx == 0:
            target = diss_path
        else:
            target = avtoref_path
        
        if not target.exists() or target.stat().st_size < 100:
            success, size = download_file(file_url, str(target))
            if success:
                downloaded = True
    
    # Save metadata
    meta = {
        "author": fullname,
        "title": title,
        "year": year,
        "source": "MSU",
        "source_url": f"https://dissovet.msu.ru/dissertation/{code}",
        "industry": subject,
        "files": {}
    }
    if diss_path.exists():
        meta["files"]["dissertation"] = "диссертация.pdf"
    if avtoref_path.exists():
        meta["files"]["avtoreferat"] = "автореферат.pdf"
    
    with open(dest_dir / "meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    if downloaded:
        stats['downloaded'] += 1
    else:
        stats['failed'] += 1
    
    if (i+1) % 20 == 0:
        log(f"[{i+1}/{len(recent)}] {fullname[:30]}... "
            f"downloaded={stats['downloaded']}, failed={stats['failed']}, skipped={stats['skipped']}")
    
    # Rate limiting
    time.sleep(0.5)

log(f"\n=== MSU Download Complete ===")
log(f"Total: {stats['total']}, Downloaded: {stats['downloaded']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
