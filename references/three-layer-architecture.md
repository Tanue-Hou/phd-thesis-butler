# Three-Layer Asset Architecture

PhD Thesis Butler v3.2 uses a three-layer asset structure for organizing Russian academic sentence templates.

## Layer Hierarchy

```
                             ┌──────────┐
                             │  GLOBAL  │  L0: Cross-cluster universal
                             │   (L0)   │      templates (quality=2 only)
                             └────┬─────┘
                                  │ zero overlap
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │TECH_LIFE │       │ HUM_SOC  │       │ART_SPORT │  L1: Discipline clusters
        │  (L1)    │       │  (L1)    │       │  (L1)    │
        └────┬─────┘       └────┬─────┘       └────┬─────┘
             │                  │                   │
             ▼                  ▼                   ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │физико-   │       │историче- │       │(future)  │  L2: Per-discipline
        │мат. науки│       │ские науки│       │          │      files
        ├──────────┤       ├──────────┤       └──────────┘
        │химические│       │филологи- │
        │науки     │       │ческие    │
        ├──────────┤       ├──────────┤
        │...       │       │...       │
        └──────────┘       └──────────┘
```

## Layer Assignment Rules

Per `LAYER_ASSIGNMENT_RULES.md`:

### Rule A → DISCIPLINE (L2)
- Template appears in exactly 1 discipline (`D_total = 1`) with ≥2 papers
- OR `dominant_discipline_share ≥ 0.7`

### Rule B → CLUSTER (L1)
- Template appears in exactly 1 cluster (`C_total = 1`) but ≥2 disciplines

### Rule C → GLOBAL (L0)
- Template appears in ≥2 clusters (`C_total ≥ 2`)
- OR is a writing-functional category (TRANSITION, CONNECTIVE, CONSERVATIVE)
- Must have quality_score = 2

## Current Build (v3.2)

| Layer | Name | Entries | Q2 | Description |
|-------|------|---------|-----|-------------|
| L0 | GLOBAL | 185 | 185 (100%) | Cross-cluster universal templates |
| L1 | TECH_LIFE | 5,699 | ~3,800 | Technical/life/precision sciences |
| L1 | HUM_SOC | 4,035 | ~2,400 | Humanities/social sciences |
| L1 | ART_SPORT | 0 | — | No art/sport data in current corpus |
| L1 | MATH_PHYS | 0 | — | Under construction (data in TECH_LIFE) |
| L2 | DISCIPLINE | ~8,000+ | ~6,500 | 34 subject-specific files |
| | **Total unique** | **17,039** | **~10,711** | **Zero overlap across layers** |

## Directory Layout

```
assets/
├── global/
│   ├── master/
│   │   ├── MASTER.jsonl         (L0: cross-cluster templates)
│   │   └── UTILS.jsonl          (functional language)
│   └── quality/                 (Q2-filtered per category)
├── cluster/
│   ├── TECH_LIFE/
│   │   ├── master/MASTER.jsonl  (L1: technical cluster)
│   │   └── quality/             (per-category Q2 files)
│   ├── HUM_SOC/
│   │   ├── master/MASTER.jsonl  (L1: humanities cluster)
│   │   └── quality/             (per-category Q2 files)
│   ├── ART_SPORT/               (placeholder)
│   └── MATH_PHYS/               (placeholder)
└── discipline/                  (L2: 34 subject JSONL files)
```

## Maintenance Notes

- **Zero overlap** across layers is enforced at generation time and verified by G4 gate.
- New data (Phase 3+) should follow the same pipeline: extract → G1/G2 → classify → G3 merge → G4 layer assign → G5 smoke test.
- Quality files can be regenerated from master files using `scripts/generate_quality.py` (if exists) or the v3.1.1 fix script.
- Language purity must be verified after any data addition using `scripts/lang_purity_check.py`.
