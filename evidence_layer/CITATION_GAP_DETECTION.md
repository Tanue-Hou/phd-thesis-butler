# Citation Gap Detection Rules

> Version: 1.0 | Claim type detection and citation necessity rules

---

## Part 1: Claim Type Detection

Each sentence in the thesis is classified into a `claim_type`. The detection uses keyword patterns and sentence structure analysis.

### Claim Types

#### 1. factual_claim
States a verifiable fact that requires a source.

**Keywords/Patterns (EN)**: "is defined as", "was established in", "consists of", "according to", "was founded in", "has been shown"
**Keywords/Patterns (RU)**: "составляет", "был основан", "согласно", "определяется как", "было показано", "установлено"
**Example (RU)**: "BERT представляет собой трансформер-энкодер, обученный на корпусе из 3.3 млрд слов."
**Required Evidence Roles**: definition, empirical_support, benchmark

#### 2. methodological_claim
Describes or justifies a method, technique, or design choice.

**Keywords/Patterns (EN)**: "we use", "we adopt", "we employ", "the method", "algorithm", "approach", "pipeline", "we implement"
**Keywords/Patterns (RU)**: "мы используем", "применяется метод", "алгоритм", "подход", "пайплайн", "мы реализуем"
**Example (RU)**: "Для разбиения текста на чанки используется рекурсивный сплиттер с overlap."
**Required Evidence Roles**: method_basis, method_comparison

#### 3. evaluative_claim
Makes a judgment about quality, performance, or effectiveness.

**Keywords/Patterns (EN)**: "outperforms", "better than", "improves", "superior", "effective", "significant", "robust"
**Keywords/Patterns (RU)**: "превосходит", "лучше чем", "улучшает", "эффективный", "значительный", "устойчивый"
**Example (RU)**: "Предлагаемый подход значительно улучшает точность поиска по сравнению с BM25."
**Required Evidence Roles**: benchmark, empirical_support, validation_standard

#### 4. gap_claim
Identifies a limitation or absence in existing work.

**Keywords/Patterns (EN)**: "remains unexplored", "lack of", "few studies", "not yet addressed", "gap", "limited research", "understudied"
**Keywords/Patterns (RU)**: "остаётся неизученным", "недостаток", "мало исследований", "ещё не решено", "пробел", "ограниченные исследования"
**Example (RU)**: "Проблема верификации генерируемых цитат в RAG-системах остаётся недостаточно исследованной."
**Required Evidence Roles**: research_gap, empirical_support

#### 5. contribution_claim
States the novelty or contribution of the current work.

**Keywords/Patterns (EN)**: "we propose", "our contribution", "novel", "first to", "we introduce", "we present", "this work advances"
**Keywords/Patterns (RU)**: "мы предлагаем", "наш вклад", "новый", "впервые", "мы вводим", "мы представляем"
**Example (RU)**: "В данной работе мы предлагаем новый подход к автоматической верификации цитат."
**Required Evidence Roles**: contribution_positioning, method_comparison

#### 6. theoretical_claim
States a theoretical principle, framework, or model.

**Keywords/Patterns (EN)**: "theory suggests", "framework", "model predicts", "principle", "hypothesis", "theoretically"
**Keywords/Patterns (RU)**: "теория предполагает", "рамки", "модель предсказывает", "принцип", "гипотеза"
**Example (RU)**: "Согласно теории информации, энтропия текста связана с его информационной ёмкостью."
**Required Evidence Roles**: structure_reference, definition

#### 7. descriptive_claim
Describes the system, process, or dataset without making an evaluative argument.

**Keywords/Patterns (EN)**: "consists of", "includes", "contains", "is composed of", "the system", "the dataset"
**Keywords/Patterns (RU)**: "состоит из", "включает", "содержит", "система", "набор данных"
**Example (RU)**: "Система состоит из трёх модулей: парсера, индексатора и генератора."
**Required Evidence Roles**: definition, method_basis (if describing a known system); not_needed (if describing own system architecture)

#### 8. common_knowledge
Statements that are widely known and do not require citation.

**Keywords/Patterns (EN)**: General facts taught in introductory courses, universally accepted definitions
**Keywords/Patterns (RU)**: Общеизвестные факты, базовые определения из учебников
**Example (RU)**: "Python является интерпретируемым языком программирования."
**gap_status**: not_needed

---

## Part 2: Citation Necessity Rules

### Decision Flowchart

```
For each sentence in thesis text:
  1. Classify claim_type
  2. IF claim_type = common_knowledge → gap_status = not_needed
  3. IF claim_type = descriptive_claim AND describes own system → gap_status = not_needed
  4. IF claim_type = descriptive_claim AND describes external system → NEEDS CITATION
  5. For all other claim_types → NEEDS CITATION
  6. For claims needing citation:
     a. Determine required_evidence_roles from claim_type
     b. Check if existing bindings cover all required roles
     c. Assign gap_status:
        - All roles covered with strength ≥ medium → covered
        - Some roles covered but weak → partial
        - No roles covered → missing
```

### Additional Necessity Signals

**NEEDS citation if sentence contains**:
- Quotation marks (direct quotes)
- "According to [Author]"
- Specific statistics or numbers ("73% of researchers...")
- Named methods, algorithms, or frameworks not invented by the author
- Claims about other researchers' work

**Does NOT NEED citation if**:
- Describing the structure of the current thesis ("В главе 3 описана...")
- Describing the author's own implementation details
- Transitional or connective sentences
- Common knowledge (see above)

---

## Part 3: Risk Level Assignment

Each gap is assigned a `risk_level` based on claim type and chapter:

| claim_type | Ch.1-2 | Ch.3-4 | Ch.5-6 | Ch.7-8 |
|---|---|---|---|---|
| factual_claim | high | high | critical | high |
| methodological_claim | medium | critical | high | medium |
| evaluative_claim | medium | medium | critical | high |
| gap_claim | critical | high | medium | high |
| contribution_claim | high | medium | medium | critical |
| theoretical_claim | high | critical | medium | medium |
| descriptive_claim | low | medium | low | low |

**Risk levels**: critical > high > medium > low

**Action by risk level**:
- **critical**: Must resolve before any chapter can be marked complete
- **high**: Should resolve before moving to Polishing Mode
- **medium**: Resolve during polishing; acceptable to note as acknowledged limitation
- **low**: Optional; resolve if time permits
