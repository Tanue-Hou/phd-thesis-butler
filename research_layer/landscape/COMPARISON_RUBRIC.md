# Comparison Rubric

> phd-thesis-butler v5.4.0 | research_layer/landscape

## Purpose

The comparison rubric defines how the agent analyzes a corpus of dissertation records to produce the landscape report. It specifies what to compare, how to cluster, and what to extract.

---

## Analysis Dimensions

The rubric operates across 7 dimensions:

```
1. Chapter Structure Comparison
2. Methodology Landscape Identification
3. Validation / Argumentation Pattern Extraction
4. Theme Clustering
5. User Positioning & Gap Identification
6. Borrowable Writing Move Detection
7. Risk Warning Generation
```

---

## 1. Chapter Structure Comparison

### Goal

Identify common dissertation structures in the corpus — how chapters are organized, what is standard vs. unusual.

### Process

1. For each record with `toc` data, normalize chapter titles
2. Map chapters to canonical types:
   - `introduction` — Введение / Introduction
   - `literature_review` — Обзор литературы / Literature Review
   - `theory` — Теоретические основы / Theoretical Foundations
   - `methodology` — Методология / Methodology / Математическое моделирование
   - `chapter_experiment` — Экспериментальные исследования / Experimental Studies
   - `chapter_results` — Результаты / Results / Результаты исследования
   - `discussion` — Обсуждение / Discussion
   - `conclusion` — Заключение / Conclusion
   - `appendix` — Приложения / Appendices
   - `other` — Anything not matching above

3. Compute frequency of each chapter type across the corpus
4. Identify 2–4 dominant structure patterns (templates)

### Output Format

```json
{
  "structure_patterns": [
    {
      "pattern_id": "standard_ru_5ch",
      "label": "Standard Russian 5-Chapter",
      "frequency": 0.45,
      "chapters": [
        "introduction",
        "literature_review",
        "methodology",
        "chapter_results",
        "conclusion"
      ],
      "typical_institutions": ["Bauman MSTU", "MADI"],
      "notes": "Most common structure for engineering dissertations"
    }
  ]
}
```

---

## 2. Methodology Landscape Identification

### Goal

Map what methodological approaches are used across the corpus, their frequency, and combinations.

### Process

1. Extract method references from `methods` field and `abstract` text
2. Classify into methodology families:
   - `mathematical_modeling` — Analytical/differential equation models
   - `simulation` — Computational simulation (MATLAB/Simulink, etc.)
   - `kalman_filtering` — Kalman filter variants (EKF, UKF, etc.)
   - `experimental_testing` — Physical experiments, bench tests
   - `machine_learning` — Neural networks, SVM, random forests, etc.)
   - `statistical_analysis` — Regression, ANOVA, hypothesis testing
   - `fem_analysis` — Finite element methods
   - `optimization` — Genetic algorithms, gradient methods, etc.
   - `data_driven` — Purely data-driven approaches
   - `hybrid` — Combination of the above

3. Count frequency of each family
4. Identify common method combinations
5. Note emerging vs. established methods

### Output Format

```json
{
  "methodology_patterns": [
    {
      "method_id": "kalman_filtering",
      "label": "Kalman Filtering Variants",
      "frequency": 0.35,
      "sub_methods": ["EKF", "UKF", "particle filter"],
      "often_combined_with": ["simulation", "experimental_testing"],
      "trend": "established",
      "typical_validation": "simulation_then_bench"
    }
  ]
}
```

---

## 3. Validation / Argumentation Pattern Extraction

### Goal

Understand how dissertations in this domain validate their claims — what constitutes sufficient evidence.

### Process

1. Extract validation type from `validation_type` field
2. Classify into validation families:
   - `simulation_only` — Results validated only via simulation
   - `simulation_then_bench` — Simulation first, then bench/stand validation
   - `simulation_then_field` — Simulation first, then real-world testing
   - `experimental_only` — Purely experimental approach
   - `mathematical_proof` — Formal mathematical proofs
   - `case_study` — Real-world case study analysis
   - `comparative_analysis` — Comparison with existing methods
   - `statistical_validation` — Statistical significance testing

3. Map validation families to chapter structures
4. Identify the "gold standard" validation in this domain
5. Note validation gaps (what's accepted but weak)

### Output Format

```json
{
  "validation_patterns": [
    {
      "pattern_id": "sim_then_bench",
      "label": "Simulation → Bench Validation",
      "frequency": 0.40,
      "description": "Numerical simulation in MATLAB/Simulink followed by experimental validation on physical test bench",
      "expected_chapters": ["methodology", "chapter_experiment", "chapter_results"],
      "strength": "high",
      "typical_claims": "Method accuracy within X% of experimental data"
    }
  ]
}
```

---

## 4. Theme Clustering

### Goal

Group dissertations into thematic clusters to reveal sub-domains and research threads.

### Process

1. Extract topics from `title`, `abstract`, `keywords`, `specialty_name`
2. Use semantic similarity to group records into clusters
3. Name each cluster with a descriptive label
4. Compute cluster size and recency (average year)
5. Identify hot (growing) vs. cold (stable) themes

### Output Format

```json
{
  "theme_clusters": [
    {
      "cluster_id": "vehicle_dynamics_estimation",
      "label": "Vehicle Dynamics State Estimation",
      "size": 4,
      "avg_year": 2018,
      "trend": "growing",
      "representative_keywords": ["vehicle state", "dynamics", "estimation"],
      "record_ids": ["dc-001", "dc-003", "dc-007", "z-002"],
      "gap_description": "Most focus on passenger vehicles; commercial vehicles underrepresented"
    }
  ]
}
```

---

## 5. User Positioning & Gap Identification

### Goal

Identify where the user's topic fits relative to the corpus, and where there are gaps.

### Process

1. Compare user's topic against theme clusters
2. Map user's intended methodology against methodology patterns
3. Identify:
   - **Overcrowded areas** — Many dissertations, hard to differentiate
   - **Under-explored areas** — Few dissertations, opportunity for novelty
   - **Methodology gaps** — Approaches not yet applied to this topic
   - **Validation gaps** — Weak validation standards that could be improved
   - **Cross-domain gaps** — Connections to adjacent fields not yet made

### Output Format

```json
{
  "positioning_gaps": [
    {
      "gap_id": "commercial_vehicle_underrepresented",
      "type": "population_gap",
      "description": "Only 1 of 10 dissertations focuses on commercial vehicles",
      "novelty_potential": "high",
      "recommendation": "Position thesis around heavy commercial vehicles"
    }
  ]
}
```

---

## 6. Borrowable Writing Move Detection

### Goal

Identify reusable writing patterns from the corpus — how authors handle specific sections, transitions, and argumentation.

### Process

1. Scan abstracts and available text for structural patterns
2. Identify:
   - **Opening moves** — How authors frame their problem statement
   - **Literature positioning** — How they position against prior work
   - **Method justification** — How they justify method choice
   - **Result presentation** — How they structure results chapters
   - **Limitation acknowledgment** — How they handle limitations
   - **Contribution statements** — How they state novelty

### Output Format

```json
{
  "borrowable_moves": [
    {
      "move_id": "problem_gap_opening",
      "type": "opening_move",
      "description": "Start with industry statistics on the problem, then narrow to the specific gap",
      "example_sources": ["dc-002", "dc-005"],
      "applicability": "high",
      "chapter": "introduction"
    }
  ]
}
```

---

## 7. Risk Warning Generation

### Goal

Alert the user to potential pitfalls based on patterns observed in the corpus.

### Process

1. Check for:
   - **Methodology saturation** — If the user's chosen method is overused
   - **Weak validation risk** — If the field accepts weak validation, the user may need to exceed it
   - **Overlap risk** — If the user's topic is very close to recent dissertations
   - **Institutional bias** — If certain structures are institution-specific and the user is at a different institution
   - **Trend misalignment** — If the user is pursuing a declining research direction
   - **Scope risk** — If similar dissertations were much broader or narrower

### Output Format

```json
{
  "risk_warnings": [
    {
      "risk_id": "methodology_saturation",
      "severity": "medium",
      "description": "Kalman filtering is used in 35% of dissertations in this domain; differentiation will require either novel application or hybrid approach",
      "mitigation": "Consider combining Kalman filtering with machine learning for novelty"
    }
  ]
}
```

---

## Recommended Outline Generation

Based on the above analyses, the rubric generates a `recommended_outline` that is directly mappable to planning_layer chapter types:

```json
{
  "recommended_outline": [
    {
      "chapter_number": 1,
      "title": "State of the Art and Problem Statement",
      "planning_layer_type": "literature_review",
      "rationale": "Standard in 90% of corpus; addresses positioning gap identified",
      "structure_confidence": 0.9,
      "evidence_layer_route": true
    },
    {
      "chapter_number": 2,
      "title": "Mathematical Model of Vehicle Dynamics",
      "planning_layer_type": "theory",
      "rationale": "Theory chapter expected in engineering dissertations",
      "structure_confidence": 0.85,
      "evidence_layer_route": false
    }
  ]
}
```

---

## Evidence Layer Routes

Each chapter in the recommended outline is flagged for evidence_layer integration:

- `evidence_layer_route: true` — This chapter needs empirical evidence binding
  - The agent should route evidence collection tasks for this chapter
- `evidence_layer_route: false` — This chapter is theory/methodology only
  - No evidence binding needed at landscape stage

---

## Weighting & Confidence

When analyzing records with varying `structure_confidence`:

| Confidence Range | Weight in Analysis |
|---|---|
| 0.9–1.0 | Full weight (1.0) |
| 0.7–0.9 | High weight (0.8) |
| 0.4–0.7 | Medium weight (0.5) |
| 0.0–0.4 | Low weight (0.2) |

Records with `structure_confidence < 0.3` are included in counts but excluded from pattern inference.
