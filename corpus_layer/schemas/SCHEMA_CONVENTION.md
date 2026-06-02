# Schema Convention — PhD Thesis Butler v4.0 Corpus Layer

## ID 命名规则
```
{source_type}_{incremental_id}
例: paper_0001, structure_0042, methodology_0017
```

## Category 枚举
```
INTRO / SURVEY / MODEL / METHOD / EXPERIMENT / RESULT / DISCUSSION / CONCLUSION
TRANSITION / FORMAL_DEFS / ENGINEERING / AREF / UTILS
```

## Cluster 枚举
```
TECH_LIFE / HUM_SOC / ART_SPORT / MATH_PHYS / GLOBAL
```

## evidence_count 字段格式
```json
{
  "count": 0,
  "source": "pending",
  "confidence": "high" | "medium" | "low" | "pending"
}
```

## source/private/public 边界
- **source 字段**: 私有构建时关联原始论文ID；公共输出时用 `"abstracted"` 替代
- **private 字段**: 以 `_internal` 后缀标记，不出现在公共资产中
- **public 字段**: 只含抽象结构、模板、统计、规则

## schema_version
```
"4.0"
```

## 文件命名规则
- schema 文件: `{domain}.schema.json`
- 记录文件: `{domain}_records.jsonl`
- 公共资产: `{domain}_v4.json`
