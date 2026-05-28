# PhD Thesis Butler — 使用说明

## 快速开始

### 1. 我在写论文，需要句式模板
1. 确定当前在写哪个部分（引言/综述/建模/...）
2. 查看 CROSS_CATEGORY_MAP.md → 找到对应的 category.subtype
3. 加载对应子 skill：`skill_view("phd-thesis-butler/sub_skills/dis_intro")`
4. 在子 skill 的 references/ 中检索：
   - `grep -i "motivation" references/QUALITY2_SELECTION.jsonl`
   - 或查看 `references/TOP50.md`

### 2. 我需要抽取新论文的句式
1. 将 PDF 命令为 P###_DIS.pdf / P###_AREF.pdf
2. 创建 batch JSON：
```json
[{"paper_id":"301","dis":"/path/P301_DIS.pdf","aref":"/path/P301_AREF.pdf"}]
```
3. 调用 GM prompt → 输出 plan → 执行子任务

### 3. 我要检查覆盖缺口
```bash
python3 scripts/coverage_check.py --input curated/master/MASTER_SENTENCEBANK_DIS.jsonl --output gaps/gap_DIS.json
```

## 分类树速查

### DIS（11 categories）
INTRO → SURVEY → MODEL → METHOD → EXPERIMENT → RESULT → DISCUSSION → CONCLUSION → TRANSITION → FORMAL_DEFS → ENGINEERING

### AREF（14 categories）
АКТУАЛЬНОСТЬ → ОБЪЕКТ_ПРЕДМЕТ → ЦЕЛЬ_ЗАДАЧИ → МЕТОДЫ → НОВИЗНА → НОВИЗНА_ФОРМУЛИРОВКИ → ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ → ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ → ПОЛОЖЕНИЯ → РЕЗУЛЬТАТЫ → АПРОБАЦИЯ → ПУБЛИКАЦИИ → СТРУКТУРА → ВЫВОДЫ

### UTIL（3 kinds）
CONNECTIVE | CONSERVATIVE | NUMERIC

## 质量等级
- 2：可直接使用，通用性强
- 1：需要人工调整场景
- 0：不进主库（存 review 分区）

## 文件检索指南
```bash
# 按 subtype 搜索
grep '"subtype":"motivation"' references/FULL_INDEX.jsonl

# 按质量筛选
grep '"quality_score":2' references/QUALITY2_SELECTION.jsonl

# 按 category 统计
python3 -c "import json; from collections import Counter; c=Counter(); [c.update([json.loads(l)['category']]) for l in open('references/FULL_INDEX.jsonl')]; print(c)"
```
