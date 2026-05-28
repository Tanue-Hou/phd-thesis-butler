# 博士论文管家（PhD Thesis Butler）

**语言：** 中文 | [English](README.md)

一个面向**俄语学术写作**的 skill-pack：从鲍曼（BMSTU）大量 кандидат/доктор 学位论文中抽取可迁移的**句式模板库（Sentencebank）**，按 DIS（论文本体结构）与 AREF（автореферат 模块）双通道分类组织，并可作为 Hermes / Claude Code / Codex 等代理的可加载"技能库"。

> 项目只提供**可迁移表达模式（模板）**，不复制原文，不输出可识别原段落。

---

## 概览

**语料与产物（当前构建）：**

- 来源论文：**327（BMSTU）**
- 模板总量：**9,602**
  - DIS 通道：**5,621**（按论文结构章节）
  - AREF 通道：**3,573**（按 автореферат 模块）
  - UTILS 通道：**408**（连接词 / 保守措辞 / 数字汇报）
- Quality=2（高可迁移精选）：**~2,000+**
- 覆盖分类/模块：**23**

每条模板包含：
- 俄语句式模式（含槽位 `[...]`）
- `when_to_use` 使用场景
- `common_mistakes` 常见误用提醒
- `quality_score`（0–2）

---

## 分类体系

### DIS 通道：按论文章节（11 类）

- INTRO（引言）
- SURVEY（综述）
- FORMAL_DEFS（定义/符号/定理）
- MODEL（建模）
- METHOD（方法/算法）
- ENGINEERING（工程实现）
- EXPERIMENT（实验/仿真）
- RESULT（结果汇报）
- DISCUSSION（讨论与解释）
- TRANSITION（段落/章节过渡）
- CONCLUSION（结论与展望）

### AREF 通道：按 автореферат 模块（14 模块）

包含：актуальность、новизна、цель/задачи、объект/предмет、методы、положения、достоверность、理论/实践意义、апробация、внедрение、структура、выводы 等。

### UTILS 通道：工具型表达（3 类）

- CONNECTIVE：转折/递进/因果/让步/举例/顺序组织
- CONSERVATIVE：保守措辞、限定条件、不确定性表达
- NUMERIC：数字结果汇报（提升/误差/分布/对比等）

---

## 质量分级（quality_score）

- **2（优秀）**：跨学科更通用，基本可直接填槽使用
- **1（可用）**：需要一定领域适配
- **0（信息性）**：领域绑定更强，需要人工挑选

---

## 数据格式（JSONL v2.1）

示例：

```json
{
  "id": "DIS_INTRO_0427",
  "text": "В последние годы [Область] привлекает всё большее внимание исследователей в связи с [Фактор/Причина].",
  "source": "DIS",
  "category": "INTRO",
  "quality_score": 2,
  "when_to_use": "用于引言开头：用"关注度上升"来引出 актуальность",
  "common_mistakes": "不要反复使用；一篇引言建议 1–2 次即可"
}
```

主库文件：

- `data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl`
- `data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl`
- `data/curated/master/MASTER_UTILS.jsonl`

精选：

- `data/curated/quality/QUALITY2_SELECTION_DIS.jsonl`
- `data/curated/quality/QUALITY2_SELECTION_AREF.jsonl`
- `data/curated/quality/QUALITY2_UTILS.jsonl`

---

## 安装

### Hermes（skill install）

```bash
hermes skill install github:Tanue-Hou/phd-thesis-butler
```

会话中加载：

```
/skill phd-thesis-butler
```

### Claude Code

```bash
mkdir -p ~/.claude/skills/
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git ~/.claude/skills/phd-thesis-butler
```

在 CLAUDE.md 中引用（示例）：

```
Always load ~/.claude/skills/phd-thesis-butler/SKILL.md for Russian academic writing.
```

### Codex CLI

```bash
git clone https://github.com/Tanue-Hou/phd-thesis-butler.git
```

---

## 用法

加载 skill 后，代理可以根据你当前写作上下文（例如 INTRO/MODEL/RESULT）推荐少量模板，供你填槽润色。

也可以直接检索：

```bash
grep '"category":"INTRO"' data/curated/quality/QUALITY2_SELECTION_DIS.jsonl | head -5
```

或加载某个子 skill：

```
/skill phd-thesis-butler/sub_skills/dis_intro
```

---

## 子技能（按写作章节）

- `sub_skills/dis_intro`
- `sub_skills/dis_survey`
- `sub_skills/dis_model`
- `sub_skills/dis_method`
- `sub_skills/dis_experiment`
- `sub_skills/dis_result`
- `sub_skills/dis_discussion`
- `sub_skills/dis_conclusion`
- `sub_skills/dis_transition`
- `sub_skills/dis_formal_defs`
- `sub_skills/dis_engineering`
- `sub_skills/aref_core`
- `sub_skills/utils_core`

---

## 免责声明（重要）

本仓库提供的是**句式模板与写作表达模式**，主要用于润色、改写、写作提示与结构化检索；并不保证任何输出可以直接作为论文/学位论文/投稿文章的最终正文提交。

使用者必须自行承担并完成：

- 事实核对、引用核查、格式与规范合规
- 重复率/相似性自检与必要的改写
- 学术诚信与原创性保障

如果你将 AI 生成文本或未审阅的模板填充内容直接用于学术提交，由此产生的一切学术与法律风险由使用者自行承担。

---

## 许可证

**CC BY 4.0** — 可自由使用、改编、再分发，需保留署名。

模板从 BMSTU 公开论文材料中提取。所有个人标识符已替换为占位符。

---

## 引用

```bibtex
@misc{phd-thesis-butler-2025,
  author = {Hou, Tianyu},
  title = {PhD Thesis Butler: Russian Academic Writing Sentence Templates},
  year = {2025},
  howpublished = {\url{https://github.com/Tanue-Hou/phd-thesis-butler}}
}
```
