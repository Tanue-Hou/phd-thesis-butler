#!/usr/bin/env python3
"""
clean_cjk_pollution.py — CJK Cleanup Script for PhD Thesis Butler
==================================================================
Scans all JSONL files under assets/ and performs two actions:

1. METADATA CLEANUP:
   - In fields: function, when_to_use, common_mistakes
   - Detect CJK characters (U+4E00–U+9FFF, U+3400–U+4DBF)
   - Replace CJK text with Russian equivalent description

2. TEMPLATE LANGUAGE TAGGING:
   - Check the 'template' field for non-Russian content (English / CJK)
   - If template contains significant non-Russian text, set 'v5_lang': 'mixed'
   - Pure Russian templates get 'v5_lang': 'ru'

Author: 明轩 (Mingxuan)
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# --- Constants ---
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CJK_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]')  # Ideographs + CJK punctuation
CJK_PUNCT_PATTERN = re.compile(r'[\u3000-\u303f\uff00-\uffef]')  # CJK punctuation only
CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04ff]')
LATIN_PATTERN = re.compile(r'[a-zA-Z]')

# Metadata fields to scan for CJK pollution
METADATA_FIELDS = ["function", "when_to_use", "when_to_ use"]  # handle variants

# --- Translation Map: CJK → Russian ---
# Common CJK phrases found in the corpus and their Russian equivalents
CJK_TO_RU = {
    # function field
    "表示因果关系。": "Указание на причинно-следственную связь.",
    "对结论或主张进行保守陈述。": "Осторожная формулировка вывода или утверждения.",
    "用于列举步骤或流程中的顺序。": "Для перечисления шагов или этапов процесса в заданном порядке.",
    "表达因果关系": "Выражение причинно-следственной связи",
    "表达转折或对比": "Выражение противопоставления или контраста",
    "对论断进行限定，使其更严谨": "Ограничение утверждения для повышения его точности",
    "报告改进或增长幅度": "Сообщение о величине улучшения или прироста",
    "在陈述结论时加入条件限制": "Добавление условий при формулировании выводов",
    "引出后续步骤或内容": "Введение последующих шагов или содержания",
    "引出一个需要承认的事实，随后提出转折": "Введение признаваемого факта с последующим противопоставлением",
    "使陈述更加谨慎，避免绝对化": "Сделать высказывание более осторожным, избегая категоричности",
    "限定某个结论或方法的适用范围": "Ограничение области применения вывода или метода",
    "指示步骤或事件的顺序": "Указание последовательности шагов или событий",
    # when_to_use field
    "解释现象或结果产生的原因。": "Для объяснения причин возникновения явления или результата.",
    "当结论基于有限证据或存在不确定性时。": "Когда вывод основан на ограниченных данных или существует неопределённость.",
    "描述多步骤过程时，使流程清晰有序。": "При описании многоэтапного процесса для ясности и последовательности.",
    "阐述研究动机或分析问题根源时。": "При обосновании мотивации исследования или анализе корней проблемы.",
    "对比已有方法与自身方法时。": "При сопоставлении существующих методов с предлагаемым подходом.",
    "报告初步或基于有限数据的发现时。": "При сообщении о предварительных результатах или выводах на основе ограниченных данных.",
    "展示实验结果或方法优势时。": "При демонстрации экспериментальных результатов или преимуществ метода.",
    "讨论模型结果的可靠性或适用边界时。": "При обсуждении надёжности результатов модели или границ её применимости.",
    "章节过渡，引导读者关注下一部分内容。": "При переходе между разделами для направления внимания читателя.",
    "当需要先承认一个缺点或挑战，再强调方法优势时。": "Когда необходимо сначала признать недостаток или трудность, а затем подчеркнуть преимущества метода.",
    "在讨论结果或做出推论时，表达不确定性。": "При обсуждении результатов или формулировании выводов для выражения неопределённости.",
    "当需要明确指出方法的适用前提或边界时。": "Когда необходимо указать предпосылки применения метода или его границы.",
    "在描述方法或算法步骤时连接不同阶段。": "При описании шагов метода или алгоритма для связи различных этапов.",
    # common_mistakes field
    "因果关联过于武断，缺乏数据或逻辑支持": "Причинно-следственная связь устанавливается слишком категорично, без поддержки данными или логикой",
    "过度使用模糊表述，削弱了结论的力度": "Чрезмерное использование размытых формулировок ослабляет убедительность вывода",
    '步骤间使用过多"затем"，显得重复单调': "Избыточное использование «затем» между шагами создаёт монотонность",
    "因果关系过于简化或武断。": "Причинно-следственная связь упрощена или установлена категорично.",
    "转折逻辑不清晰，对比的双方不对称。": "Логика перехода неясна, сопоставляемые стороны несимметричны.",
    "过度使用模糊限定词，削弱结论力度。": "Чрезмерное использование оговорок ослабляет убедительность вывода.",
    "只报告百分比，不提供基准值或绝对值。": "Сообщается только процент без указания базового или абсолютного значения.",
    "将限制条件作为脚注，而非结论的一部分。": "Ограничения оформляются как сноски, а не как часть вывода.",
    "过渡生硬，与上下文逻辑脱节。": "Переход резкий, логически не связан с контекстом.",
}

# Patterns for partial CJK replacement (when mixed with Russian text)
PARTIAL_CJK_PATTERNS = [
    # CJK + Russian text patterns — replace just the CJK portion
    (re.compile(r'表示因果关系'), 'Причинно-следственная связь'),
    (re.compile(r'表示转折'), 'Выражение противопоставления'),
    (re.compile(r'因果关系'), 'причинно-следственная связь'),
    (re.compile(r'对比'), 'сопоставление'),
]


def has_cjk(text: str) -> bool:
    """Check if text contains CJK characters."""
    return bool(CJK_PATTERN.search(text))


def get_primary_script(text: str) -> str:
    """Determine the primary script of a text string."""
    if not text or not text.strip():
        return "empty"
    
    cyr_count = len(CYRILLIC_PATTERN.findall(text))
    lat_count = len(LATIN_PATTERN.findall(text))
    cjk_count = len(CJK_PATTERN.findall(text))
    
    total = cyr_count + lat_count + cjk_count
    if total == 0:
        return "other"
    
    # If more than 50% Cyrillic, consider it Russian
    if cyr_count / total > 0.5:
        return "ru"
    # If CJK present at all, it's mixed
    if cjk_count > 0:
        return "mixed"
    # Otherwise English/mixed
    return "mixed"


def clean_cjk_in_text(text: str) -> tuple[str, bool]:
    """
    Replace CJK text with Russian equivalent.
    Returns (cleaned_text, was_modified).
    """
    if not isinstance(text, str):
        return text, False
    
    # Strip old CJK markers from previous runs
    original_text = text
    was_marked = '[部分内容已清理]' in text or '[частично очищено]' in text
    if was_marked:
        text = text.replace(' [部分内容已清理]', '').replace('[部分内容已清理]', '')
        text = text.replace(' [частично очищено]', '').replace('[частично очищено]', '')
        text = re.sub(r'\s+', ' ', text).strip()
    
    # Try exact match first
    text_stripped = text.strip()
    if text_stripped in CJK_TO_RU:
        return CJK_TO_RU[text_stripped], True
    
    # Try with trailing punctuation variations
    for cjk, ru in CJK_TO_RU.items():
        if text_stripped == cjk.rstrip('。'):
            return ru.rstrip('.'), True
    
    # If the entire text is CJK and not in our map, provide a generic marker
    if has_cjk(text) and not CYRILLIC_PATTERN.search(text):
        # Fully CJK — replace with generic Russian placeholder
        return f"[Описание на китайском языке удалено: требуется ручной перевод]", True
    
    # Mixed text: CJK embedded in Russian — try partial replacement
    if has_cjk(text):
        modified = text
        for pattern, replacement in PARTIAL_CJK_PATTERNS:
            modified = pattern.sub(replacement, modified)
        
        # Replace CJK punctuation with Russian equivalents
        punct_map = {
            '\uff0c': ', ',  # ，→ ,
            '\u3002': '. ',  # 。→ .
            '\uff1b': '; ',  # ；→ ;
            '\u3001': ', ',  # 、→ ,
            '\uff08': '(',  # （→ (
            '\uff09': ')',  # ）→ )
            '\u300c': '"',  # 「→ "
            '\u300d': '"',  # 」→ "
            '\u300a': '"',  # 《→ "
            '\u300b': '"',  # 》→ "
        }
        for cjk_p, ru_p in punct_map.items():
            modified = modified.replace(cjk_p, ru_p)
        
        # If CJK ideographs still remain, mark and strip
        if re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', modified):
            # Strip old CJK markers from previous runs
            modified = re.sub(r'\s*\[部分内容已清理\]', '', modified)
            modified = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf]', '', modified)
            modified = re.sub(r'\s+', ' ', modified).strip()
            if modified:
                return modified + " [частично очищено]", True
            return "[смешанный контент: требуется ручной перевод]", True
        
        # Clean up old CJK markers from previous runs
        if '[部分内容已清理]' in modified:
            modified = modified.replace(' [部分内容已清理]', '').replace('[部分内容已清理]', '')
            modified = re.sub(r'\s+', ' ', modified).strip()
        
        # Clean up double spaces from punctuation removal
        modified = re.sub(r'\s+', ' ', modified).strip()
        modified = re.sub(r'\s+([,.;)])', r'\1', modified)  # no space before punct
        
        return modified, True
    
    return text, was_marked


def process_jsonl_file(filepath: Path) -> dict:
    """
    Process a single JSONL file.
    Returns stats dict.
    """
    stats = {
        "file": str(filepath),
        "total_entries": 0,
        "metadata_cleaned": 0,
        "template_marked_mixed": 0,
        "template_marked_ru": 0,
        "already_v5_lang": 0,
    }
    
    modified_lines = []
    file_modified = False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            stats["total_entries"] += 1
            entry_modified = False
            
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                modified_lines.append(line)
                continue
            
            # --- Step 1: Clean CJK from metadata fields ---
            for field in ["function", "when_to_use", "common_mistakes"]:
                if field not in entry:
                    continue
                
                value = entry[field]
                
                if isinstance(value, str):
                    cleaned, was_modified = clean_cjk_in_text(value)
                    if was_modified:
                        entry[field] = cleaned
                        entry_modified = True
                        stats["metadata_cleaned"] += 1
                
                elif isinstance(value, list):
                    list_modified = False
                    new_list = []
                    for item in value:
                        if isinstance(item, str) and has_cjk(item):
                            cleaned, was_modified = clean_cjk_in_text(item)
                            new_list.append(cleaned)
                            if was_modified:
                                list_modified = True
                                stats["metadata_cleaned"] += 1
                        else:
                            new_list.append(item)
                    
                    if list_modified:
                        entry[field] = new_list
                        entry_modified = True
            
            # Also clean CJK from 'kind' field if present
            if "kind" in entry and isinstance(entry["kind"], str) and has_cjk(entry["kind"]):
                entry["kind"] = "[удалено: CJK]"
                entry_modified = True
                stats["metadata_cleaned"] += 1
            
            # --- Step 2: Tag template language ---
            template = entry.get("template", "")
            if isinstance(template, str) and template.strip():
                if "v5_lang" in entry:
                    stats["already_v5_lang"] += 1
                else:
                    primary = get_primary_script(template)
                    if primary == "mixed" or (primary != "ru" and has_cjk(template)):
                        entry["v5_lang"] = "mixed"
                        stats["template_marked_mixed"] += 1
                        entry_modified = True
                    elif primary == "ru":
                        entry["v5_lang"] = "ru"
                        stats["template_marked_ru"] += 1
                        entry_modified = True
                    elif primary == "empty":
                        pass  # skip empty
                    else:
                        entry["v5_lang"] = "mixed"
                        stats["template_marked_mixed"] += 1
                        entry_modified = True
            
            if entry_modified:
                file_modified = True
            
            modified_lines.append(json.dumps(entry, ensure_ascii=False))
    
    # Write back if modified
    if file_modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in modified_lines:
                f.write(line + '\n')
    
    return stats


def main():
    """Main entry point."""
    print("=" * 70)
    print("  CJK Cleanup Script — PhD Thesis Butler")
    print("  Scanning assets/ for CJK pollution in JSONL files")
    print("=" * 70)
    print()
    
    if not ASSETS_DIR.exists():
        print(f"ERROR: Assets directory not found: {ASSETS_DIR}")
        sys.exit(1)
    
    # Find all JSONL files
    jsonl_files = sorted(ASSETS_DIR.rglob("*.jsonl"))
    print(f"Found {len(jsonl_files)} JSONL files to process.")
    print()
    
    # Aggregate stats
    total_stats = {
        "files_processed": 0,
        "files_modified": 0,
        "total_entries": 0,
        "metadata_cleaned": 0,
        "template_marked_mixed": 0,
        "template_marked_ru": 0,
        "already_v5_lang": 0,
    }
    
    file_results = []
    
    for filepath in jsonl_files:
        stats = process_jsonl_file(filepath)
        file_results.append(stats)
        total_stats["files_processed"] += 1
        total_stats["total_entries"] += stats["total_entries"]
        total_stats["metadata_cleaned"] += stats["metadata_cleaned"]
        total_stats["template_marked_mixed"] += stats["template_marked_mixed"]
        total_stats["template_marked_ru"] += stats["template_marked_ru"]
        total_stats["already_v5_lang"] += stats["already_v5_lang"]
        
        if stats["metadata_cleaned"] > 0 or stats["template_marked_mixed"] > 0:
            total_stats["files_modified"] += 1
            rel_path = filepath.relative_to(ASSETS_DIR)
            print(f"  [MODIFIED] {rel_path}")
            print(f"    entries={stats['total_entries']} | "
                  f"metadata_cleaned={stats['metadata_cleaned']} | "
                  f"templates_mixed={stats['template_marked_mixed']} | "
                  f"templates_ru={stats['template_marked_ru']}")
    
    # Print summary
    print()
    print("=" * 70)
    print("  CLEANUP SUMMARY")
    print("=" * 70)
    print(f"  Files scanned:           {total_stats['files_processed']}")
    print(f"  Files modified:          {total_stats['files_modified']}")
    print(f"  Total entries processed: {total_stats['total_entries']}")
    print(f"  Metadata fields cleaned: {total_stats['metadata_cleaned']}")
    print(f"  Templates tagged 'mixed':    {total_stats['template_marked_mixed']}")
    print(f"  Templates tagged 'ru':       {total_stats['template_marked_ru']}")
    print(f"  Already had v5_lang:         {total_stats['already_v5_lang']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
