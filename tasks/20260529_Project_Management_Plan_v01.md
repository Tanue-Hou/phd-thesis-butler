# PhD Thesis Butler — 项目管理与工作流规范

> **适用对象：** 思远及所有子智能体
> **目标：** 所有命令/脚本运行写日志，所有变更进 Git 版本管理

---

## 一、项目 Git 初始化

**目的：** 跟踪所有脚本、日志、配置、报告的版本变化

### Task 1: 初始化 Git 仓库（已完成）

```bash
cd /mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler
git init
git add PROJECT.md reports/ scripts/ tasks/
git commit -m "init: project structure + scripts + reports"
```

**当前状态：** ✅ 已初始化，main 分支

### Task 2: 添加 .gitignore

```bash
cat > .gitignore << 'EOF'
# Logs - keep git clean
logs/*.log
logs/*.pid

# Data - too large for git
data/MSU/*
data/SPbSU/*
data/BMSTU/*

# But keep meta structure
!data/MSU/.gitkeep
!data/SPbSU/.gitkeep
!data/BMSTU/.gitkeep

# Temp files
*.tmp
*.temp
__pycache__/
*.pyc
EOF

git add .gitignore
git commit -m "chore: add .gitignore (exclude data + logs)"
```

---

## 二、日志规范

**目的：** 每条命令执行、每个脚本运行都留下可追溯的记录

### 日志目录结构

```
logs/
├── operations.log        ← 所有手动命令的日志
├── msu_download.log      ← МГУ 下载脚本日志
├── spbu_download.log     ← СПбГУ 下载脚本日志
├── bmstu_organize.log    ← BMSTU 整理日志
└── quality_check.log     ← 质量检查日志
```

### 手动命令日志格式

每次通过 terminal 执行有意义的操作后，同步写入 `logs/operations.log`：

```
[2026-05-29 19:00] ACTION: 启动 МГУ 下载脚本
  CMD: python3 scripts/download_msu_v2.py
  PID: 23167
  STATUS: running

[2026-05-29 19:30] ACTION: 停止 МГУ 下载
  CMD: kill 23167
  STATUS: stopped (580/1581 complete)

[2026-05-29 20:00] ACTION: BMSTU 数据整理
  CMD: python3 scripts/organize_bmstu.py
  STATUS: complete (327 dissertations organized)
```

### 脚本自动日志

每个脚本在运行时自动写入其专属日志文件：
- 使用 `>> logfile 2>&1` 重定向
- 脚本内部使用 `log(msg)` 函数输出时间戳 + 进度信息
- 关键节点（启动/完成/错误）必须记录

---

## 三、Git 提交流程

### 提交触发条件

以下变更必须提交 Git：

| 变更类型 | 提交时机 | 示例 |
|----------|---------|------|
| 脚本修改 | 每次修改后 | `git commit -m "fix: shorten timeouts in MSU downloader"` |
| 报告输出 | 每次新报告 | `git commit -m "docs: add expansion investigation report"` |
| 配置文件 | 每次修改后 | `git commit -m "chore: update .gitignore"` |
| 项目元数据 | PROJECT.md 变更 | `git commit -m "docs: update project status"` |
| 任务文档 | 每次新计划 | `git commit -m "docs: add download implementation plan"` |

### 不提交的内容

- ❌ `logs/` 目录（运行日志不进入 Git）
- ❌ `data/` 目录（论文 PDF 太大，不进 Git）
- ❌ 临时文件

### 提交频率

- 每个 Task 完成后立即提交
- 不做「攒了一堆改完再提交」

---

## 四、当前项目状态（便于后续追踪）

| 日期 | 操作 | 结果 |
|------|------|------|
| 2026-05-29 | 创建项目结构 + Git 初始化 | ✅ PROJECT.md, reports/, scripts/, tasks/ |
| 2026-05-29 | 完成各大学公开来源调研 | ✅ reports/ 下 |
| 2026-05-29 | 下载 СПбГУ 论文 | ✅ 727 篇 |
| 2026-05-29 | 下载 МГУ 论文 | ⏸ 580/1,581（暂停） |
| 2026-05-29 | BMSTU 数据整理 | ✅ 327 篇，按学科归类 |
| 2026-05-29 | 质量检查 | ✅ 1,250 篇验证通过 |
| 2026-05-29 | 制定项目管理规范 | 📝 本文档 |
