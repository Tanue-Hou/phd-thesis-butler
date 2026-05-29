# Layer Assignment Rules — 模板归层一般规则

## 核心公式

对每条模板，计算其在语料库中的分布：

| 变量 | 含义 |
|------|------|
| `D_total` | 出现该模板的不同学科数量 |
| `C_total` | 出现该模板的不同大类数量 |
| `dominant_cluster_share` | 模板在最主要大类的占比 |
| `dominant_discipline_share` | 模板在最主要学科的占比 |

## 归层优先级（从最专有到最通用）

### Rule A → DISCIPLINE (L2)

满足任一：

1. `D_total = 1` 且该学科论文覆盖 ≥2 篇
2. `dominant_discipline_share ≥ 0.7` 且 `C_total = 1`
3. 学科专有关键词（强规则）：
   - MEDICINE: критерии включения/исключения, этический комитет
   - ECONOMICS: эндогенность, идентификация, робастность
   - MATHEMATICS: лемма, теорема, доказательство
   - ARTS: творческий метод, художественный анализ

### Rule B → CLUSTER (L1)

满足全部：

1. `C_total = 1`（只在一个大类出现）
2. `D_total ≥ 2`（至少 2 个不同学科）
3. `dominant_cluster_share ≥ 0.8`

### Rule C → GLOBAL (L0)

满足任一：

1. `C_total ≥ 2`（跨两个或三个大类）
2. 虽然 `C_total = 1`，但属于「写作通用功能」且跨学科覆盖极高：
   - TRANSITION / CONNECTIVE / CONSERVATIVE
   - RESULT.numeric_reporting 通用口径

## 写作功能偏置（layer_bias）

边界情况用偏置裁决：

| 偏置方向 | 类别 / subtype |
|----------|---------------|
| → DISCIPLINE | EXPERIMENT.data_description, METHOD.identification_strategy, FORMAL_DEFS.{lemma,proof}, 医学伦理/纳排 |
| → GLOBAL | TRANSITION, CONNECTIVE, CONSERVATIVE, RESULT.numeric_reporting 通用口径 |

当 Rules A/B/C 边界模糊时，按 layer_bias 决策。

## 去重与归并

1. 只在同一 `category/subtype` 内做
2. 归一化：去空格、统一标点、统一 `[...]`
3. 近似重复合并为一个「主模板」，保留 2-3 个「变体」
4. 变体不跨层：同一语义簇只能落在一个层级

## 质量门控

| quality | 归层限制 |
|---------|---------|
| 2 | 可进入任意层 |
| 1 | 倾向留在 DISCIPLINE 或 CLUSTER |
| 0 | 不参与自动归层，仅 review |

进入 GLOBAL 的模板必须 quality≥2。

## 最小阈值（开箱即用）

```
D_total = 1                          → DISCIPLINE
C_total = 1 且 D_total ≥ 2           → CLUSTER
C_total ≥ 2                          → GLOBAL
dominant_discipline_share ≥ 0.7      → 强制 DISCIPLINE
dominant_cluster_share ≥ 0.8         → 强制 CLUSTER
边界情况                               → layer_bias 决策
```
