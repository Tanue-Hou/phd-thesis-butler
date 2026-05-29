# Changelog

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
