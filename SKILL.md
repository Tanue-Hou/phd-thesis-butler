---
name: phd-thesis-butler-polish
description: "俄语学术写作润色系统 — 加载即用，自动学科匹配+句式模板+润色"
version: "1.0"
---

# PhD Thesis Butler — Russian Academic Writing Assistant

## 用户无感使用说明

**只需两步：**
1. 加载本 skill（`/skill phd-thesis-butler-polish`）
2. 丢入俄语论文段落 → 自动输出润色文本

**系统自动完成：**
- 推断学科方向（理工/医学/经济/人文…）
- 识别写作场景（INTRO/MODEL/EXPERIMENT/RESULT/DISCUSSION/CONCLUSION）
- 三层回退检索模板（L2学科→L1大类→L0通用）
- 润色文本 + 改动摘要

---

## 工作流

```
用户输入（段落/文件）
  │
  ▼
① Router — 学科推断 + 场景推断
  ├─ 学科: project_config > 文件路径 > 关键词 > 默认(TECH_LIFE)
  └─ 场景: INTRO/MODEL/EXPERIMENT/RESULT/DISCUSSION/CONCLUSION/...
  │
  ▼
② Retriever — 三层回退检索
  ├─ L2(DISCIPLINE).QUALITY2  → 命中即停
  ├─ L1(CLUSTER).QUALITY2     → 回退
  └─ L0(GLOBAL).QUALITY2      → 最终回退
  │
  ▼
③ Polisher — 三级润色
  ├─ L1: 语言润色（默认，不改结构/结论）
  ├─ L2: 结构润色（需用户触发）
  └─ L3: 学术重写（需用户确认）
  │
  ▼
④ Consistency — 术语/符号/引用一致性检查
⑤ Safety/QA — 不引入新事实、不夸大
  │
  ▼
输出: 润色文本 + 改动摘要(3行)
```

---

## Router 输入/输出契约

### Router 输入（来自用户文本）

```json
{
  "text": "原文段落...",
  "filepath": "путь/к/файлу.pdf",
  "config": "project_config.yaml"
}
```

### Router 输出（plan JSON）

```json
{
  "discipline_inference": {
    "cluster": "TECH_LIFE",
    "discipline": "ENGINEERING",
    "confidence": 0.85
  },
  "scene_inference": {
    "category": "INTRO",
    "subtype": "motivation",
    "confidence": 0.7
  },
  "polish_level": "L1",
  "plan": [
    {"step": "retrieve_templates", "fallback_chain": ["DISCIPLINE(ENGINEERING).QUALITY2", "CLUSTER(TECH_LIFE).QUALITY2", "GLOBAL.QUALITY2"]},
    {"step": "polish_text", "level": "L1"},
    {"step": "consistency_check"},
    {"step": "safety_check"}
  ]
}
```

---

## 默认策略

| 条件 | 行为 |
|------|------|
| 学科未命中（confidence < 0.5） | 默认 TECH_LIFE，走 CLUSTER→GLOBAL 回退 |
| 学科命中 | L2(DISCIPLINE) 命中即停，不查 L1/L0 |
| L2 为空 | 无声回退到 L1/L0，用户无感 |
| 场景未命中 | 默认 INTRO/general |
| L1/L0 也为空 | 返回"当前无匹配模板，建议补充学科数据" |

---

## 输出格式

### 成功

```
📝 润色后文本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[润色后的段落]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ 改动摘要
• 术语统一: [具体改动]
• 连接结构改善: [具体改动]
• 结论措辞更克制: [具体改动]
```

### 失败（模板为空）

```
⚠️ 当前无匹配模板，已用通用语言规则润色。
建议补充 [学科] 数据以获得学科化润色。
```

---

## 最小用例

### 用例 1: INTRO（引言）

```
输入: "Актуальность данной работы обусловлена потребностью в повышении точности управления."
输出: L1 语言润色 + 3行改动摘要
```

### 用例 2: MODEL（模型）

```
输入: "Пусть x(t) — вектор состояния системы, u(t) — управление."
输出: L1 语言润色 + 术语一致性检查
```

### 用例 3: RESULT（结果）

```
输入: "Эксперимент показал, что предложенный метод лучше."
输出: L1 润色（"лучше"→"обеспечивает более высокую точность"）+ 保守措辞提醒
```

---

## 文件结构

```
agents/
├── router/router_agent.py        ← 学科+场景推断
├── retriever/retriever_agent.py  ← 三层回退检索
├── polisher/polisher_agent.py    ← 三级润色
├── consistency/consistency_agent.py ← 一致性检查
└── safety/safety_agent.py        ← 安全审查
assets/
├── global/                        ← L0: 跨学科通用 (9,602 templates)
├── cluster/TECH_LIFE/            ← L1: 理工农医大类 (9,602 templates)
└── discipline/                    ← L2: 具体学科 (待填充)
project_config.yaml                ← 用户学科配置
```

---

## 约束

- 不引入新事实、新数据、新引用
- 不改变论文结论
- 不输出抄袭句式
- 学科数据未填充时无声回退到通用层
