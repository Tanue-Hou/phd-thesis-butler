# Dissertation Landscape Report: Vehicle State Estimation

> **Topic:** Vehicle state estimation and identification using Kalman filtering methods
> **User Direction:** Developing a novel adaptive Kalman filtering approach for real-time vehicle state estimation using multi-sensor fusion on commercial vehicles
> **Generated:** phd-thesis-butler v5.4.0 demo | All data fabricated for demonstration

---

## 1. Corpus Overview

**Total records analyzed:** 18 dissertations and related works

| Source | Records |
|---|---|
| DisserCat | 10 |
| Zotero private corpus | 8 |

**Read depth distribution:**

| Read Depth | Count | % |
|---|---|---|
| Title only | 2 | 11% |
| Abstract + TOC | 11 | 61% |
| Full metadata | 3 | 17% |
| Fulltext | 2 | 11% |

**Degree types:** 10 candidate dissertations, 8 unspecified (international works from Zotero)

**Time span:** 2017–2024, with peak activity in 2020–2023

**Institutions represented:** МАДИ, МГТУ им. Баумана, СПбПУ, ТГУ, and others; international works from TU Munich, KAIST, RWTH Aachen, Tsinghua

---

## 2. Theme Clusters

Five distinct thematic clusters were identified in the corpus:

### Cluster A: Vehicle Dynamics State Estimation (6 records, growing)

Core topic of the corpus. Covers estimation of vehicle states (speed, yaw rate, sideslip angle, tire forces) using Kalman filter variants. Predominantly focused on passenger vehicles. Average year 2020, indicating active research area.

**Key gap:** Commercial and heavy vehicles are severely underrepresented — only 1 record out of 6 addresses this population.

### Cluster B: Machine Learning for Vehicle Diagnostics (4 records, growing)

Applies ML methods (CNN, LSTM, XGBoost) to vehicle component diagnostics and state prediction. Average year 2021. These approaches show high accuracy but are typically standalone — not integrated with traditional Kalman-based estimation frameworks.

**Key gap:** No work combines ML-based process noise estimation with adaptive Kalman filtering.

### Cluster C: Navigation and Positioning for Autonomous Vehicles (3 records, growing)

Focuses on navigation state estimation (position, heading) for autonomous vehicles using GNSS/INS integration. Uses Kalman filtering but for navigation rather than vehicle dynamics.

**Key gap:** Bridge between navigation-level and vehicle-dynamics-level estimation is missing.

### Cluster D: Component Degradation and Remaining Life (2 records, stable)

Statistical approaches to predicting component remaining useful life. Uses Bayesian methods and regression analysis. Average year 2018, suggesting a mature but less active area.

**Key gap:** No integration with real-time state estimation; operates in offline mode.

### Cluster E: Kalman Filter Variants Comparison (3 records, stable)

Systematic comparison studies of EKF vs. UKF vs. other variants for vehicle applications. Provides methodological foundations but does not propose novel estimation frameworks.

**Key gap:** No systematic framework for method selection based on vehicle type and operating conditions.

---

## 3. Structure Patterns

Four dominant dissertation structures were identified:

### Pattern 1: Standard Russian 5-Chapter (45%)

`Introduction → Literature Review → Methodology → Results → Conclusion`

The most common structure for Russian engineering candidate dissertations. Found at МАДИ, Баумана, Политех. Follows the conventional ВАК format. Typically 120–150 pages.

### Pattern 2: Extended Russian 6-Chapter (30%)

`Introduction → Literature Review → Theory → Methodology → Results → Conclusion`

Adds a separate theory chapter for mathematical foundations. Common when the mathematical model is a significant part of the contribution. Found at Баумана and СПбПУ.

### Pattern 3: International 6-Chapter (15%)

`Introduction → Literature Review → Methodology → Results → Discussion → Conclusion`

Western-style structure with an explicit Discussion chapter. Found in international theses from TU Munich, KAIST, RWTH Aachen. Typically includes a broader literature positioning and more explicit limitations discussion.

### Pattern 4: Minimal 4-Chapter (10%)

`Literature Review → Methodology → Results → Conclusion`

Compressed structure with shorter length. Found at regional technical universities. May signal narrower scope or shorter dissertations.

---

## 4. Methodology Landscape

### Dominant Methods

**Kalman Filtering Variants (65%)** — The backbone of the field. EKF is the most common (40%), followed by UKF (25%), with particle filters and adaptive variants emerging. Typically combined with simulation modeling.

**Computational Simulation (75%)** — MATLAB/Simulink is ubiquitous. CarSim and Adams are used for vehicle dynamics simulation. Nearly every dissertation includes a simulation component.

**Physical Experimental Testing (55%)** — Test benches, real vehicle tests, and dynamometer testing. Split between bench validation and full vehicle road tests.

### Emerging Methods

**Machine Learning (25%)** — CNN, LSTM, XGBoost applied to vehicle diagnostics. Growing trend (avg year 2021) but not yet dominant. Typically used for classification rather than continuous state estimation.

**Multi-Sensor Fusion (35%)** — IMU+GPS, camera+LiDAR fusion architectures. Growing in importance as autonomous driving research matures.

### Method Combinations

The most common combination is: **KF variant + MATLAB/Simulink simulation + real vehicle testing** (found in 40% of records).

An emerging combination is: **ML + experimental testing** (found in 15% of records), typically in the diagnostics cluster.

**No record in the corpus combines: adaptive KF tuning + ML-based process noise estimation.** This represents a clear methodology gap.

---

## 5. Validation Patterns

### Pattern 1: Simulation → Real Vehicle (40%)

The gold standard in this domain. Algorithm developed and validated in MATLAB/Simulink or CarSim, then tested on a real vehicle with data acquisition. Strongest validation type. Typical claim: "Method achieves X% accuracy improvement over baseline on real vehicle data."

### Pattern 2: Simulation → Test Bench (25%)

Simulation followed by hardware-in-the-loop or component test bench validation. Slightly weaker than full vehicle testing but more controlled. Typical claim: "Bench results confirm simulation predictions within X% deviation."

### Pattern 3: Simulation Only (15%)

All validation via numerical simulation. Acceptable for methodological contributions but increasingly viewed as insufficient by reviewers. Typical claim: "Algorithm converges within X iterations with Y% accuracy."

### Pattern 4: Experimental Only (10%)

No prior simulation; method developed and validated entirely through experiments. Less common in KF-based work. Typical claim: "Experimental classification accuracy of X%."

### Pattern 5: Comparative Analysis (10%)

Systematic comparison of multiple algorithms under identical conditions. Valuable for understanding method trade-offs but does not introduce new methods. Typical claim: "Algorithm A outperforms Algorithm B by X% under condition Y."

**Recommendation:** Aim for Pattern 1 (simulation → real vehicle) to meet the highest validation standard. Budget time and resources for experimental validation from the start.

---

## 6. Methodology Gap Analysis

| Gap | Description | Novelty Potential |
|---|---|---|
| Hybrid KF+ML | No dissertation combines adaptive KF tuning with ML-based process noise estimation | **High** |
| Commercial vehicles | Only 1/18 dissertations addresses heavy commercial vehicles | **High** |
| Real-time embedded | Few demonstrate real-time implementation on vehicle ECUs | **Medium** |
| Extreme conditions | Ice, heavy rain, off-road scenarios rarely tested | **Medium** |
| Multi-modal estimation | Only 1 record uses particle filters for multi-modal distributions | **Medium** |

---

## 7. User Positioning

Your stated direction — *"novel adaptive Kalman filtering approach for real-time vehicle state estimation using multi-sensor fusion on commercial vehicles"* — positions you well:

- **Commercial vehicle focus** addresses the largest population gap
- **Adaptive KF** differentiates from static EKF/UKF approaches
- **Multi-sensor fusion** is a growing area with practical relevance
- **Real-time implementation** addresses the validation gap

### Potential Overlap Risk

Your topic is close to dc-001 (adaptive KF for passenger vehicles) and dc-003 (commercial vehicle dynamics). To differentiate:

1. Emphasize the **hybrid KF+ML** approach — no one in the corpus does this
2. Focus explicitly on **commercial vehicles** — dc-003 is the only competitor
3. Include **real-time embedded implementation** — most competitors validate offline

---

## 8. Borrowable Writing Moves

### Opening Move: Industry Statistics → Gap → Problem Statement

Start with statistics on commercial vehicle safety incidents related to state estimation failures, then narrow to the specific technical gap. Used effectively in dc-001 and dc-003. **Applicability: High.**

### Method Justification: Comparison Table

Include a table comparing candidate methods across criteria (accuracy, computational cost, robustness, implementation complexity). Used in dc-010. Helps reviewers understand why your method was chosen. **Applicability: High.**

### Result Presentation: Convergence Analysis First

Present algorithm convergence plots (estimation error vs. time) before absolute accuracy metrics. This demonstrates the algorithm works reliably before discussing precision. Used in dc-002. **Applicability: High.**

### Result Presentation: Error Budget Decomposition

Decompose total error into sensor noise, model mismatch, and algorithmic error components. Shows deep understanding of error sources. Used in zotero-ABCD1234. **Applicability: Medium.**

### Contribution Statement: Numbered Triple

State contributions as a numbered list of 3 items: (1) mathematical model, (2) algorithm, (3) experimental validation. Common in Russian dissertations. **Applicability: High.**

---

## 9. Risk Warnings

### ⚠ Methodology Saturation (Medium Severity)

Kalman filtering (EKF/UKF) is used in 65% of dissertations. Pure KF application without novelty may be seen as insufficient contribution. **Mitigation:** Differentiate through hybrid KF+ML approach or focus on commercial vehicles.

### ⚠ Validation Standard Rising (Medium Severity)

The field increasingly expects both simulation AND real vehicle validation. Simulation-only may be viewed as insufficient. **Mitigation:** Plan for real vehicle testing from the start.

### ⚠ Passenger Vehicle Overlap (High Severity)

5+ recent dissertations focus on passenger vehicle state estimation. Risk of being perceived as incremental. **Mitigation:** Explicitly differentiate by focusing on commercial vehicles and novel sensor configurations.

### ⚠ Scope Risk (Low Severity)

Covering all vehicle states plus all KF variants may be too broad. **Mitigation:** Focus on 2–3 key states and 1–2 KF variants.

---

## 10. Recommended Outline

Based on the landscape analysis, the following chapter structure is recommended:

| Ch | Title | Type | Confidence | Evidence Route |
|---|---|---|---|---|
| 1 | Обзор современных методов оценки состояния транспортных средств. Постановка задачи исследования | `literature_review` | 0.90 | ✅ Yes |
| 2 | Математическая модель динамики коммерческого транспортного средства | `theory` | 0.85 | — |
| 3 | Адаптивный алгоритм оценки состояния на основе гибридного KF-ML подхода | `methodology` | 0.90 | ✅ Yes |
| 4 | Имитационное моделирование и анализ сходимости алгоритма | `chapter_results` | 0.85 | ✅ Yes |
| 5 | Экспериментальная верификация на реальном коммерческом транспортном средстве | `chapter_results` | 0.90 | ✅ Yes |
| 6 | Заключение и направления дальнейших исследований | `conclusion` | 0.95 | — |

This follows the **Extended Russian 6-Chapter** pattern (30% of corpus) with the theory chapter separated from methodology. Chapters 4 and 5 are split to provide both simulation and experimental validation, following the gold standard (Pattern 1).

---

## 11. Evidence Layer Routes

The following chapters require evidence binding:

### Chapter 1: Literature Review
- Systematic comparison table of existing methods with quantitative metrics
- Statistics on commercial vehicle accidents / state estimation needs
- Gap analysis supported by citation count data

### Chapter 3: Methodology
- Convergence proof or analysis for the proposed algorithm
- Computational complexity analysis
- Comparison with baseline methods on benchmark scenarios

### Chapter 4: Simulation Results
- Simulation result tables and plots
- Statistical significance tests for improvement claims
- Sensitivity analysis results

### Chapter 5: Experimental Verification
- Real vehicle test data with sensor specifications
- Comparison tables: simulation vs. experimental results
- Error analysis and uncertainty quantification
- Embedded system performance metrics (latency, memory usage)

---

## 12. Summary and Next Steps

**The landscape reveals a clear opportunity:** vehicle state estimation is a well-established field dominated by EKF/UKF approaches on passenger vehicles, but commercial vehicles and hybrid KF+ML approaches are significantly underrepresented. Your positioning addresses both gaps simultaneously.

### Immediate Next Steps

1. **Feed this outline to planning_layer** — Begin detailed chapter planning
2. **Start evidence collection for Chapter 1** — Build the comparison table of existing methods
3. **Design Chapter 3 methodology** — Detail the hybrid KF+ML architecture
4. **Plan experimental setup for Chapter 5** — Identify test vehicle and sensor suite early

### Key Differentiators to Emphasize

- Commercial vehicle focus (population gap)
- Hybrid KF+ML approach (methodology gap)
- Real-time embedded implementation (validation gap)
- Adverse condition testing (scope gap)
