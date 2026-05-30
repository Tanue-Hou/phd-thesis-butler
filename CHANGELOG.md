## v3.3.4 (2026-05-30)

### Field name cleanup + validate expansion

**修复**
- 2,448 处畸形字段名修复：`when[...]to[...]use`→`when_to_use`, `paper[...]id`→`paper_id` 等
- 379 处 UTILS 中文清理：kind/when_to_use/common_mistakes 中的中文→俄语
- validate_skill_assets.py: 全 key/value 检查 + bracket in key 禁止 + 拼写变体检测
- py_compile + 6 smoke tests 全绿

## v3.3.3 (2026-05-30)

### Language purity — full CJK + spacing cleanup

**修复**
- 全库 CJK 污染清除：3,614 处中文→俄语槽位替换，不删除条目
- NO_SPACE 修复：195 处 Cyrillic/Latin 无空格混写（"ДляPRESENTACии"→"Для PRESENTACии"）
- subtype_mapping_v3.3.json + standard_taxonomy_v3.3.json 中文清除（44+100 处）
- validate_skill_assets.py 扩展：检查所有字段（subtype/function/slots/when_to_use/cm/kind/strength）及 references 文件
- retireve_templates.py 输出 CJK 过滤加强 + 元组 3 元素修复

## v3.3.2 (2026-05-30)

### Engineering fix — retrieve_templates, CJK cleanup, delegation

**修复**
- retrieve_templates.py: 元组结构修复 (score, layer_name, entry) 3元素，消除 r[3] 崩溃
- 检索逻辑改为真三级回退：DISCIPLINE ≥K → 停；不足→CLUSTER；不足→GLOBAL
- CJK 过滤：输出时过滤 template/when_to_use/common_mistakes 含中文的条目
- 全库 3,614 处中文污染清理（template 中 CJK →俄语槽位，metadata 中 CJK →[...]）
- SKILL.md description 强化：显式支持中英文触发俄语模板
- delegation.provider 统一 deepseek，子智能体继承主智能体 API
- validate_skill_assets.py 全绿通过 ✅

## v3.3.1 (2026-05-30)

### Engineering Convergence — 工程化收敛

**核心修复**
- SKILL.md: {text}→{template} schema对齐，中文/英文控制语言规则
- 13个子skill全量重写，清除死引用
- GLOBAL层计数修正 1,764→1,284
- GitHub Actions CI验证工作流新增

**新增**
- scripts/retrieve_templates.py — 确定性三层回退检索脚本
- scripts/validate_skill_assets.py — 全量资产验证（6项检查）
- evals/evals.json — 10个最小测试用例

## v3.3 (2026-05-30)

### Subtype 标准化与语义检索升级

**Subtype 精炼：**
- 6,866 个旧 subtype → 1,662 个标准化纯俄语 subtype（缩减 75.8%）
- 清除所有英/中文 subtype（431 个非俄语名→纯俄语）
- 生成标准 taxonomy（25 个 category，1,448 个标准名）
- 生成完整映射表 subtype_mapping_v3.3.json

**SKILL.md 升级：**
- 检索策略升级为双通道（精确匹配 + 语义理解）
- 智能体可理解用户意图后进行语义近似匹配
- 新增 taxonomy 参考文件说明

**数据清理：**
- 315 条数据 subtype 字段更新
- 零中文残留 ✅
- 零 JSON 解析错误 ✅

# Changelog

## v3.2.2 (2026-05-30)

### Assets Data Fix — 数据清理 + SKILL.md 检索与润色规则增强

**SKILL.md 修复与增强：**
- version: v3.2 → v3.2.2 ✅
- 检索策略：从扁平 `data/` 搜索升级为**三层回退链**（DISCIPLINE → CLUSTER → GLOBAL → data fallback）
- 润色规则：从简单 "offer to rewrite" 增强为完整约束（Do/Do NOT + 输出格式）
- Data Files Reference 表：补充 assets/ 三层路径 + data/ fallback 路径

**数据清理：**
- 删除混淆目录 `assets/cluster/GLOBAL/`（185条错误路径，合并到 assets/global/）
- GLOBAL 层整理：MASTER.jsonl 1,764 条 → 1,284 条（仅保留 Q2 跨学科模板，665 条下移至 cluster 层，备份于 MASTER_ARCHIVE.jsonl）
- 所有 34 个 discipline 文件 `_layer` 字段修复（ART_SPORT/HUM_SOC 等过期值清理）
- 所有 cluster quality 文件 `_layer`/`_discipline` 字段同步修复

**待处理：**
- `assets/discipline/биологических_наук.jsonl` 前 7 条英文模板待翻译
- subtype 命名标准化（俄/英/中文混用）
- README 数据口径待 GLOBAL 层稳定后同步

## v3.2.1 (2026-05-30)

### Document Consistency Fix — 统一数据口径 + 俄语文档

**修复（P0 — 上线阻断级）**
- README 顶部摘要统一：19,007 → **16,735**（全文档唯一真源口径）
- README Phase 4 三层架构数字对齐：GLOBAL 185 / TECH_LIFE 5,699 / HUM_SOC 4,035
- README Phase 1 语料口径澄清：1,403 篇独立论文（1,042 正文 + 361 摘要），含扫描 PDF 过滤说明
- SKILL.md 数据描述统一：17,039 → **16,735**，文件引用表同步
- 发现并修复 SKILL.md 中剩余 3 处口径不一致

**新增**
- README 俄语（Русский）章节：目标、规模、安装、3 层架构、免责声明、许可证
- README 三语切换：🇬🇧 → 🇷🇺 → 🇨🇳

**SKILL.md 已升级至 v3.2 口径：**
- version: 3.2 ✅
- 语料规模: 16,735 ✅
- 三层架构说明 ✅
- 严格语言规则（纯俄语输出）✅

## v3.2 (2026-05-30)

### Language Purity Cleanup — 纯正科研俄语

**删除/修复**
- 删除 24 条中文混入模板（汉字嵌入俄语）
- 删除 1,944 条英文模板（完整英文句子）
- 修复 1,273 处中文元数据（when_to_use/function/common_mistakes 翻译为俄语）
- SKILL.md 新增严格语言规则：所有输出必须为俄语

**数据统计**
- DIS: 11,980 → 10,124（纯俄语）
- AREF: 6,619 → 6,587（纯俄语）
- UTILS: 408 → 328（纯俄语）
- Total: 19,007 → 17,039（100% 纯正科研俄语）

## v3.1.1 (2026-05-30)

### Asset Layer Fix — 归层修复 + 占位符迁移 + PII 脱敏

**修复**
- Issue 1: HUM_SOC/ART_SPORT master/MASTER.jsonl 填充数据（原为空）
- Issue 2: GLOBAL/TECH_LIFE quality 文件消除 100% 重叠（EXPERIMENT/METHOD/MODEL/RESULT/SURVEY 按学科正确分配）
- Issue 3: 全局 UTILS 占位符统一迁移 ___ → [...]（499+493+236 处）
- Issue 4: HUM_SOC/TECH_LIFE quality 子目录生成（按 category 拆分）
- PII 脱敏检查通过（无真实人名/邮箱/电话/地址泄露）

**资产结构**
- GLOBAL (L0): 188 条（跨层级通用模板，Q2=100%）
- TECH_LIFE (L1): 5,802 条（技术/生命/精密科学）
- HUM_SOC (L1): 4,055 条（人文/社会科学）
- Zero overlap across all layers ✅

## v3.1.0 (2026-05-30)

### Phase 2 Integration — MSU + SPbSU 双通道数据合并

**新增**
- 合并 MSU + SPbSU Phase 2 抽取数据（10,045 条 → 合并后 19,007 条）
- 新增 6,621 条 DIS 模板（总计 11,980）
- 新增 3,291 条 AREF 模板（总计 6,619）
- Quality=2 selections：DIS 8,383 / AREF 2,228
- 新增参考文献：pipeline-extraction.md / dissertation-sources.md / batch-download-tips.md

**架构**
- DIS + AREF 双通道独立抽取 → 去重归并 → 归层分配 → 门控上线
- 从 BMSTU 扩展到 MSU + SPbSU（3 所高校）
- 数据源覆盖 34 学科、23 categories

**Skill 版本**
- 内置模板：9,602 → 19,007 条（+98%）
- 学科覆盖：1 校 → 3 校
- SKILL.md 更新数据引用和版本号

## v2.1.0 (2026-05-29)

### BMSTU 基线 + 13 子 Skill 架构

- 第一批 327 篇 BMSTU 论文全量抽取（9,602 条）
- 13 个子 skill 按需加载架构
- 5-Agent 润色管线：Router → Retriever → Polisher → Consistency → Safety
- 公开 README + 私有配置分层隔离
