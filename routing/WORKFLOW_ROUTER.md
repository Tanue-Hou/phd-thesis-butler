# Workflow Router — phd-thesis-butler v5.4.1

用户入口从 6 个分散模式收敛为 4 个可理解的工作流。路由规则定义了"用户说什么 → 进入哪个工作流"的判断顺序。

---

## 四个工作流

```
User request
  ├─ 1. 俄语润色与表达优化
  │    用户已有俄语文本，需要润色、改写、降 AI 味
  │    → templates + retrieve_templates.py
  │
  ├─ 2. 论文规划与结构设计
  │    用户只有研究方向/想法，需要论文结构
  │    → planning_layer + discipline assets
  │    （如果用户提了同方向论文/Zotero，先走 3 再回 2）
  │
  ├─ 3. 文献调研与论文对比
  │    用户想查文献、找同方向论文、用 Zotero
  │    → research_layer + landscape + Zotero + build_review
  │    （landscape 是文献调研的高级形态，不是独立入口）
  │
  └─ 4. 证据检查与引用修复
       用户已有章节草稿，想知道引用够不够
       → evidence_layer + citation gap + binding
```

---

## 路由优先级（判断顺序）

每次用户请求按以下顺序判断，**命中即停**：

| 优先级 | 条件 | 路由到 |
|:------:|:-----|:-------|
| **1** | 用户贴了一段俄语正文，要求润色/改写/降低机器感 | **Polishing → 1** |
| **2** | 用户贴了正文，问引用/证据/支撑够不够 | **Evidence → 4** |
| **3** | 用户提同方向论文/DisserCat/Zotero/别人怎么写 | **Research/Landscape → 3** |
| **4** | 用户问论文结构/开题/章节/实验/方法/导师汇报 | **Planning → 2** |
| **5** | 用户只问句式/表达/俄语模板 | **Template Retrieval → 1** |

### 多意图请求处理

| 用户同时要 | 处理顺序 |
|:-----------|:---------|
| 润色 + 检查引用 | 先 Evidence（检查引用）→ 后 Polishing（润色结果） |
| 规划 + 同方向论文 | 先 Landscape（搜同方向）→ 后 Planning（基于结果规划） |
| Zotero + 规划结构 | 先 Landscape（搜 Zotero）→ 后 Planning（基于文献规划） |

---

## 各 layer 的职责边界

| Layer | 角色 | 是否用户入口 |
|:------|:-----|:------------|
| `planning_layer/` | 从用户想法生成论文结构 | ✅ 工作流 2 |
| `research_layer/` + `landscape/` | 搜文献、搜同方向论文、对比分析 | ✅ 工作流 3 |
| `evidence_layer/` | 检查文献是否支撑章节、检测引用缺口 | ✅ 工作流 4 |
| `assets/references/disciplines/` | 学科范式知识资产（内部） | ❌ 不作为独立入口 |
| `retrieve_templates.py` + assets | 俄语句式模板检索（内部） | ❌ 被工作流 1 调用 |
| `research_layer/landscape/` | 文献调研的高级形态（景观分析） | ❌ 归入工作流 3 |

---

## 工作流详解

### 工作流 1：俄语润色与表达优化

**入口条件**：用户有俄语正文 → 要润色/表达优化

**流程**：
1. 检测写作章节（INTRO/SURVEY/MODEL/...）
2. 三层回退检索模板（DISCIPLINE → CLUSTER → GLOBAL）
3. 基于模板润色用户原文
4. 输出润色结果 + 修改摘要 + 命中层级

**不做的事**：
- 不新增事实、数据、引用
- 不改变作者的结论强度
- 不假定用户需要文献支撑

### 工作流 2：论文规划与结构设计

**入口条件**：用户有研究方向/想法 → 要论文结构

**流程**：
1. 判断学科大类（ENGINEERING_CONTROL 等）
2. 读取对应 cluster 规划指南
3. 选择结构模式（工程/AI/社科/...）
4. 生成 chapter blueprint
5. 选择方法论路线和实验方案
6. 构建逻辑闭环
7. 路由到句式模板检索

**注意**：如果用户同时提到"同方向论文"或"Zotero"，先走工作流 3，再回到此流程。

### 工作流 3：文献调研与论文对比

**入口条件**：用户要查文献、找同方向论文、用 Zotero

**包含**：
- 公开来源搜索（DisserCat、eLIBRARY、CyberLeninka、OpenAlex、Semantic Scholar）
- Zotero 私有文献库接入（Zotero Capability Gate → 可用降级）
- 景观分析（同方向论文结构/方法论/验证模式对比）→ 生成输出
- 基于分析结果 → 路由到规划（工作流 2）或证据绑定（工作流 4）

**read_depth 标注规则**：
- metadata_only：只读到元数据
- abstract_toc：读到摘要和目录
- zotero_indexed_fulltext：读到 Zotero 已索引全文
- fulltext_local：用户提供本地 PDF

### 工作流 4：证据检查与引用修复

**入口条件**：用户有章节草稿 → 想知道引用是否足够

**流程**：
1. 检测章节中每个论断的引用状态（covered / partial / missing / not_needed）
2. 列表现有文献能支撑什么角色
3. 标注引用缺口并推荐补充文献类型
4. 输出可读报告

**不做的事**：
- 不替代用户去搜索文献（推荐 source_type 和查询方向，不编造引用）

---

## 交叉路由示例

```
用户说："从我的 Zotero 找 vehicle estimation 论文，帮我规划章节"
  ↓
检测：Zotero + 规划 → 多意图
  ↓
先走工作流 3（Landscape）：搜 Zotero → 生成景观报告
  ↓
再走工作流 2（Planning）：基于景观报告的 recommended_outline → 细化章节
```

```
用户说："帮我润色这段俄语引言，顺便检查引用够不够"
  ↓
检测：润色 + 检查引用 → 多意图
  ↓
先走工作流 4（Evidence）：检查引用缺口 → 生成报告
  ↓
再走工作流 1（Polishing）：润色正文 ← 证据报告补充引用建议
```
