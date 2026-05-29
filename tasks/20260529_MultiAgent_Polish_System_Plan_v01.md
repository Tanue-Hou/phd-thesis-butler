# 俄语学术写作润色系统 — 多智能体实施计划

> **工作流遵循：** plan → git commit → execute → log → git commit
> **模型：** mimo-v2.5（所有子智能体）
> **项目位置：** `D:\Hermes\01_Active_Projects\PhD_Thesis_Butler\`

---

## 一、系统架构（5 Agent Pipeline）

```
用户输入（段落/文件/章节）
  │
  ▼
┌─────────────────────────────────────┐
│  ① Router Agent                     │
│  ├─ 判断学科 (discipline inference)  │
│  ├─ 判断场景 (section inference)     │
│  └─ 输出执行计划 JSON                │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  ② Retriever Agent                  │
│  ├─ A: discipline + QUALITY2 + cat  │
│  ├─ B: global + QUALITY2 + cat      │
│  ├─ C: discipline + QUALITY1 + cat  │
│  └─ D: global + QUALITY1 + cat      │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  ③ Polisher Agent                   │
│  ├─ Level 1: 语言润色（默认）        │
│  ├─ Level 2: 结构润色               │
│  └─ Level 3: 学术化重写（谨慎）      │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  ④ Consistency Agent                │
│  ├─ 术语/符号一致性检查              │
│  ├─ 引用口径一致性检查               │
│  └─ 学科风格对齐                    │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  ⑤ Safety/QA Agent                  │
│  ├─ 不引入新事实/新结论              │
│  ├─ 不过度承诺/夸大                  │
│  ├─ 不输出抄袭句式                   │
│  └─ 风险提示（合规/引用）             │
└─────────────────────────────────────┘
  │
  ▼
输出：润色后文本 + 改动摘要（极简）
```

---

## 二、各 Agent 职责

### 1. Router Agent

**输入：** 用户文本 + 上下文
**输出：** `{discipline, category, subtype, level, plan: [...]}`

```
判断流程：
① 检查 project_config.yaml（如存在，固定学科）
② 检查文件路径/目录名
③ 从文本前500字提取关键词
④ 若仍不确定，默认 tech（工程背景）

场景检测（关键词匹配）：
  актуальность/цель/задачи → INTRO
  пусть/обозначим/предположим → MODEL/FORMAL_DEFS
  эксперимент/выборка/метрики → EXPERIMENT
  табл./рис./RMSE/ошибка → RESULT
  ограничения/перспективы → DISCUSSION/CONCLUSION
```

### 2. Retriever Agent

**输入：** `{discipline, category, subtype, quality_level}`
**输出：** 3-5 条最佳匹配模板

```
检索顺序（A+B 策略）：
  1. data/{discipline}/quality/QUALITY2_{cat}.jsonl
  2. data/global/quality/QUALITY2_{cat}.jsonl
  3. data/{discipline}/master/MASTER_{cat}.jsonl
  4. data/global/master/MASTER_{cat}.jsonl

学科强差异模块（优先走学科库）：
  - медицина: этика, критерии включения/исключения
  - экономика: эндогенность, робастность
  - math_phys: леммы/теоремы
  - humanities: методологическая позиция
```

### 3. Polisher Agent

**输入：** 原文 + 模板集
**输出：** 润色后文本

```
三级策略：
  Level 1（默认）：语法/用词/连接/冗余
  Level 2：重排句序/增加过渡句
  Level 3（需用户确认）：学术化重写

模板使用方式（非复制）：
  - 用模板校正表达强度
  - 用模板校正连接词
  - 用模板校正限定条件（UTIL.CONSERVATIVE）
  - 用模板校正结果汇报口径（UTIL.NUMERIC）
```

### 4. Consistency Agent

**输入：** 原文 + 润色后文本
**输出：** 一致性报告

```
检查项：
  - 术语是否全文统一
  - 符号/缩写是否一致
  - 引用口径是否一致（如引用格式）
  - 学科风格是否对齐
```

### 5. Safety/QA Agent

**输入：** 原文 + 润色后文本
**输出：** 安全报告

```
检查项：
  - ❌ 不引入新事实/新结论
  - ❌ 不添加新引用
  - ❌ 不过度承诺（强度从 strong→conservative 需标记）
  - ✅ 风险提示（如"此句需引用来源"）
```

---

## 三、与现有数据结构的对接

现有数据路径：

```
data/
├── BMSTU/               ← 按学科已分类
├── MSU/                 ← 按学科已分类
├── SPbSU/               ← 按学科已分类
└── [新建] global/       ← 跨学科通用模板（从现有 MASTER 提取）
└── [新建] discipline_specific/  ← 按学科筛选的精选子集
```

需要新增：
- `scripts/router_agent.py`
- `scripts/retriever_agent.py`  
- `scripts/polisher_agent.py`
- `scripts/consistency_agent.py`
- `scripts/safety_agent.py`
- `SKILL.md`（主 Router skill，供加载即用）
- `project_config.yaml`（用户确认学科后固定）

---

## 四、实施步骤（按 Task 拆分）

### Task 1: 创建项目结构
- 新建 `agents/` 目录
- 创建 `project_config.yaml` 模板
- git commit

### Task 2: 编写 Router Agent
- 学科推断模块
- 场景检测模块
- 输出执行计划 JSON
- git commit

### Task 3: 编写 Retriever Agent
- A+B 检索逻辑
- 学科库 vs 全局库回退
- git commit

### Task 4: 编写 Polisher Agent
- 三级润色策略
- 模板校正逻辑
- git commit

### Task 5: 编写 Consistency + Safety Agents
- 一致性检查
- 安全/合规检查
- git commit

### Task 6: 编写主 SKILL.md（Router skill）
- 供用户加载即用
- 自动串联 5 agent pipeline
- git commit

### Task 7: 测试验证
- 用 BMSTU 数据做端到端测试
- git commit

---

## 五、时间预估

| Task | 内容 | 预估 |
|------|------|------|
| T1 | 项目结构 + config | 0.5h |
| T2 | Router Agent | 1h |
| T3 | Retriever Agent | 1h |
| T4 | Polisher Agent | 1.5h |
| T5 | Consistency + Safety | 1h |
| T6 | SKILL.md Router skill | 0.5h |
| T7 | 测试验证 | 1h |
| **合计** | | **~6.5h** |

---

## 六、风险与控制

| 风险 | 应对 |
|------|------|
| delegate_task provider 问题 | 先修 delegation 配置或直接串行调用 |
| 学科库数据不足（如医学库为0） | 回退到 global 库，标记"需人工确认" |
| PDF 无法解析 | 先用 txt/md 文本测试，PDF 解析后续加 |
| mimo-v2.5 输出不稳定 | 每个 agent 输出加 JSON schema 校验 |
