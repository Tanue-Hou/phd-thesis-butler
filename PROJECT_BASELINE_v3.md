# PhD Thesis Butler — Project Baseline v3.0

## 1. 三层资产定义与互斥性（硬约束）

| 层 | 标识 | 内容 | 互斥规则 |
|----|------|------|---------|
| L0 GLOBAL | `assets/global/` | 跨学科通用模板（TRANSITION, CONNECTIVE, CONSERVATIVE, 通用 INTRO） | 不得出现在 CLUSTER 或 DISCIPLINE |
| L1 CLUSTER | `assets/cluster/{NAME}/` | 大类通用模板（TECH_LIFE / HUM_SOC / ART_SPORT） | 不得出现在 GLOBAL 或 DISCIPLINE |
| L2 DISCIPLINE | `assets/discipline/{NAME}/` | 具体学科专有模板（MEDICINE / ECONOMICS / …） | 不得出现在 GLOBAL 或 CLUSTER |

**验证：** `smoke_test.sh` 检查各层 MASTER.jsonl 的 template hash，zero overlap 为通过门槛。

## 2. 占位符规范（硬约束）

- 全库唯一占位符：`[...]`
- 禁止：`___`、`[___]`、`{...}`、`<...>`
- QA 扫描：`grep -c '___' assets/*/master/MASTER.jsonl` 必须返回 0

## 3. 命中阈值与回退规则（硬约束）

```
L2(DISCIPLINE).QUALITY2 → 取 ≥3 条？→ 是 = 停止
  ↓ 否
L1(CLUSTER).QUALITY2    → 补到 3 条？→ 是 = 停止
  ↓ 否
L0(GLOBAL).QUALITY2     → 补到 3 条？→ 是 = 停止
  ↓ 否
L2(DISCIPLINE).QUALITY1 → 补到 3 条
  ↓
L1(CLUSTER).QUALITY1    → 补到 3 条
  ↓
L0(GLOBAL).QUALITY1     → 最后保障
```

**命中定义：** 在对应层级的 QUALITY2_{CAT}.jsonl 中检索到 ≥3 条同 category 模板。

## 4. 输出字段（硬约束）

每次输出必须包含：

```json
{
  "polished": "润色后文本",
  "changes": ["改动1", "改动2", "改动3"],
  "hit_layer": "CLUSTER|GLOBAL|DISCIPLINE",
  "hit_quality": 2,
  "hit_count": 3,
  "cluster": "TECH_LIFE",
  "discipline": "ENGINEERING",
  "category": "INTRO",
  "subtype": "motivation"
}
```

任何一个字段缺失 = fail。

## 5. 回退链

加载顺序：L2 → L1 → L0，quality 优先 Q2 → Q1。

## 6. 外部依赖

- 核心流程（路由、检索、润色）不依赖外部 provider
- 外部 API 仅作为可选开发工具
- smoke_test 不得因网络波动失败

## 7. 版本号规则

- 格式：`v{major}.{minor}.{patch}`
- major：架构变更
- minor：资产/规则扩展
- patch：Bug 修复
- 当前：**v3.0.0**
