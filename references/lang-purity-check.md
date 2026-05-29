# Language Purity Checking Methodology

Used in v3.2 cleanup to ensure 100% pure Russian templates (removed 24 CN + 1,944 EN + 44 garbage).

## 5-Pass Detection Pipeline

### Pass 1 — CJK Character Detection (template field)
```
CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
```
Scans the `template` field for any Chinese, Japanese, or Korean characters. Entries with hits are removed entirely (template contamination cannot be repaired — the template is fundamentally bilingual).

### Pass 2 — English Template Detection (academic English)
```
is_real_english_template(text):
  1. Strip all [...] and ___ placeholders
  2. Count Cyrillic vs Latin letters in remaining text
  3. If > 60% Latin AND contains ≥2 English function words → English
```
Catches full English sentence templates like "The dataset consists of ___ trajectories..." English function words checked: `the, is, are, was, were, has, have, been, this, that, with, from, for, and, but, not, its, it, of, in, on, at, by, to, we, our, an, a, as, be, they`.

### Pass 3 — Chinese Metadata Remediation
For `when_to_use`, `function`, `common_mistakes` fields: scan for CJK characters. Replace affected values with `[...]` placeholder (preserves the entry's Russian template while removing Chinese instructions). Counter: 1,273 entries fixed.

### Pass 4 — Aggressive English Detection (short forms)
Edge cases missed by Pass 2 (short templates, templates using `[...]` instead of `___`):
```
is_english_aggressive(text):
  1. Strip ALL placeholder patterns: [...], ___, ..., {}
  2. If zero Cyrillic AND ≥3 Latin characters → English
  3. If Latin > 40% of letters AND ≥2 English function words → English
```
This catches templates like "We define ___ as ___." and "Future work should focus on ___."

### Pass 5 — Garbage/Invalid Entry Removal
Entries with:
- No real content (< 3 non-placeholder characters)
- URL artifacts (http://, www.)
- Mostly symbols (> 70% non-alpha characters)
Removed as they provide no useful template value.

## Verification Gate
After all 5 passes, re-scan the entire corpus with both CJK and English detectors. Zero hits = verified clean. Log the pass/fail status in CHANGELOG.

## When to Re-run
Re-run this pipeline whenever:
- New PDF sources are ingested (new university batch)
- New templates are extracted (new batch from LLM)
- Before any release/tag that claims "pure Russian" status
