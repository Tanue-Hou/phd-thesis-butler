#!/usr/bin/env python3
"""
SPbSU Dissertation Downloader
Downloads full dissertations from disser.spbu.ru
Organizes by: data/SPbSU/{subject}/{author}/
"""

import subprocess, json, re, os, time, sys
from pathlib import Path
from collections import defaultdict

BASE = "/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler/data/SPbSU"

def log(msg):
    print(f"[SPbSU] {msg}")
    sys.stdout.flush()

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

def get_author_folder(fullname):
    # Use the Russian name part (before /)
    name = fullname.split('/')[0].strip()
    return sanitize_filename(name.replace(' ', '_'))

def download_file(url, filepath, max_retries=3):
    full_url = f"https://disser.spbu.ru{url}" if url.startswith('/') else url
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "30", full_url, "-o", filepath, "-w", "%{http_code}"],
                capture_output=True, text=True, timeout=35
            )
            if result.stdout == "200":
                size = os.path.getsize(filepath)
                if size > 1000:
                    return True, size
            if os.path.exists(filepath) and os.path.getsize(filepath) < 100:
                os.remove(filepath)
        except:
            pass
        if attempt < max_retries - 1:
            time.sleep(2)
    return False, 0

# Step 1: Get all author IDs from listing pages
log("Scanning SPbSU listing pages...")
all_ids = []
for start in range(0, 1420, 20):
    url = f"https://disser.spbu.ru/dissertatsionnye-sovety-spbgu/proshedshie-zashchity-dissertatsij.html?start={start}"
    try:
        result = subprocess.run(["curl", "-s", "-L", "--max-time", "10", url],
                              capture_output=True, text=True, timeout=12)
        html = result.stdout
        ids = re.findall(r'/zashchita-uchenoj-stepeni-spbgu/(\d+)-[^"]*\.html', html)
        all_ids.extend(ids)
    except:
        pass
    if (start // 20) % 10 == 0:
        log(f"  Scanned pages up to start={start}, found {len(all_ids)} authors")

all_ids = list(set(int(x) for x in all_ids))
all_ids.sort()
log(f"Total SPbSU authors found: {len(all_ids)}")

# Step 2: Visit each author page, extract info, download
stats = {"processed": 0, "downloaded": 0, "failed": 0, "skipped": 0, "recent": 0, "old": 0}

for i, aid in enumerate(all_ids):
    url = f"https://disser.spbu.ru/zashchita-uchenoj-stepeni-spbgu/{aid}.html"
    try:
        result = subprocess.run(["curl", "-s", "-L", "--max-time", "10", url],
                              capture_output=True, text=True, timeout=12)
        html = result.stdout
    except:
        stats['failed'] += 1
        continue
    
    # Extract metadata
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text_clean = re.sub(r'<[^>]+>', '\n', text)
    lines = [l.strip() for l in text_clean.split('\n') if l.strip()]
    
    # Extract full name - must be a line with translit
    fullname = ""
    for l in lines:
        if '/ ' in l and not any(x in l for x in ['Научная', 'научная', 'специальность', 'Диссертация', 'диссертация']):
            parts = l.split('/')
            if len(parts) >= 2 and len(parts[0].strip().split()) >= 2:
                fullname = parts[0].strip()
                break
    
    # Also try to get fullname from title tag
    if not fullname:
        titles = re.findall(r'<title>([^<]*)</title>', html)
        if titles:
            t = titles[0].split('/')[0].strip()
            if len(t.split()) >= 2:
                fullname = t
    
    if not fullname:
        stats['failed'] += 1
        continue
    
    # Extract defense date
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', html)
    defense_year = 0
    for d in dates:
        try:
            y = int(d.split('.')[-1])
            if 2000 <= y <= 2026:
                defense_year = y
                break
        except:
            pass
    
    # Filter by year
    if defense_year < 2023 or defense_year > 2026:
        stats['old'] += 1
        stats['skipped'] += 1
        continue
    stats['recent'] += 1
    
    # Extract subject from "кандидата XXX наук" or "доктора XXX наук"
    subject = "другие_науки"
    for l in lines:
        m = re.search(r'(?:кандидата|доктора)\s+([а-яё]+\s+наук)', l)
        if m:
            subject = m.group(1).replace(' ', '_')
            break
    
    # Extract title
    title = ""
    for l in lines:
        if 'Тема:' in l or 'Theme:' in l:
            title = l.replace('Тема:', '').replace('Theme:', '').strip()
            title = re.sub(r'[\xab\xbb\u201c\u201d\u2018\u2019"\']', '', title)
            break
    
    # Extract PDF links
    # Look for "Диссертация / Dissertation" links
    pdf_links = re.findall(r'href="([^"]*\.pdf)"[^>]*>[^<]*Диссертация[^<]*</a>', html, re.IGNORECASE)
    if not pdf_links:
        pdf_links = re.findall(r'href="([^"]*\.pdf)"', html)
        # Filter out known non-dissertation PDFs
        pdf_links = [l for l in pdf_links if not any(x in l for x in ['otzyv', 'otziv', 'prikaz', 'diplom', 'zayavlenie', 'spisok'])]
    
    if not pdf_links:
        stats['failed'] += 1
        stats['skipped'] += 1
        continue
    
    # Create directories
    author_folder = get_author_folder(fullname)
    # Sanity check: author folder must be reasonable length
    if len(author_folder) > 80 or len(author_folder) < 5:
        stats['failed'] += 1
        stats['skipped'] += 1
        continue
    subject_folder = subject
    dest_dir = Path(BASE) / subject_folder / author_folder
    
    # Skip if already downloaded
    if (dest_dir / "диссертация.pdf").exists() and (dest_dir / "meta.json").exists():
        stats['skipped'] += 1
        continue
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    diss_path = dest_dir / "диссертация.pdf"
    avtoref_path = dest_dir / "автореферат.pdf"
    
    # Download files
    downloaded = False
    for pdf_url in pdf_links[:2]:  # max 2 files
        if not pdf_url.startswith('http'):
            pdf_url = f"https://disser.spbu.ru{pdf_url}"
        
        target = diss_path if not diss_path.exists() or diss_path.stat().st_size < 100 else avtoref_path
        
        if not target.exists() or target.stat().st_size < 100:
            success, size = download_file(pdf_url, str(target))
            if success:
                downloaded = True
    
    # Save metadata
    meta = {
        "author": fullname,
        "title": title,
        "year": defense_year,
        "source": "SPbSU",
        "source_url": url,
        "industry": subject.replace('_', ' '),
        "vak_code": "",
        "degree": "",
        "files": {}
    }
    if diss_path.exists() and diss_path.stat().st_size > 1000:
        meta["files"]["dissertation"] = "диссертация.pdf"
    if avtoref_path.exists() and avtoref_path.stat().st_size > 1000:
        meta["files"]["avtoreferat"] = "автореферат.pdf"
    
    with open(dest_dir / "meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    if downloaded:
        stats['downloaded'] += 1
    else:
        stats['skipped'] += 1
    
    stats['processed'] += 1
    if (i+1) % 20 == 0:
        log(f"[{i+1}/{len(all_ids)}] {fullname[:30]}... "
            f"recent={stats['recent']}, down={stats['downloaded']}, fail={stats['failed']}")
    
    time.sleep(0.3)

log(f"\n=== SPbSU Download Complete ===")
log(f"Total: {len(all_ids)}, Recent(2023-2026): {stats['recent']}, "
    f"Downloaded: {stats['downloaded']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
