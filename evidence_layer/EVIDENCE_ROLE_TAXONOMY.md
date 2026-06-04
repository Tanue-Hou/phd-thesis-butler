# Evidence Role Taxonomy

> Version: 1.0 | Status: Canonical Reference

This document defines the 12 evidence roles used throughout the PhD Thesis Butler evidence layer. Each role specifies the function a cited source plays in supporting a scholarly claim.

---

## 1. background_context

- **Definition**: Provides general domain knowledge or situational framing that orients the reader to the topic area. Not directly arguing a point but establishing the landscape.
- **Applicable Chapters**: Ch.1 Introduction, Ch.2 Literature Review, Ch.7 Discussion
- **Example (RU)**: "В последние годы внимание к автоматизации научных исследований значительно возросло [Author, Year]."

---

## 2. research_gap

- **Definition**: Identifies an unexplored area, unresolved question, or limitation in existing work that justifies the current study.
- **Applicable Chapters**: Ch.1 Introduction, Ch.2 Literature Review
- **Example (RU)**: "Несмотря на значительный прогресс в области LLM, проблема верификации генерируемых текстов остаётся недостаточно изученной [Author, Year]."

---

## 3. definition

- **Definition**: Provides authoritative definitions of key terms, concepts, or constructs used in the thesis.
- **Applicable Chapters**: Ch.1 Introduction, Ch.3 Methodology, Ch.4 System Architecture
- **Example (RU)**: "Под Retrieval-Augmented Generation (RAG) понимается подход, при котором генеративная модель дополняется внешними знаниями из базы данных [Lewis et al., 2020]."

---

## 4. method_basis

- **Definition**: Cites the original source or canonical reference for a method, algorithm, or technique adopted in this work.
- **Applicable Chapters**: Ch.3 Methodology, Ch.4 System Architecture, Ch.5 Implementation
- **Example (RU)**: "Для эмбеддинга документов используется модель sentence-transformers, предложенная Reimers & Gurevych [2019]."

---

## 5. method_comparison

- **Definition**: References work that compares alternative methods, justifying the selection of one approach over others.
- **Applicable Chapters**: Ch.3 Methodology, Ch.7 Discussion
- **Example (RU)**: "Сравнение BM25 и dense retrieval показывает преимущество последнего в задачах семантического поиска [Thakur et al., 2021]."

---

## 6. benchmark

- **Definition**: Cites established benchmarks, datasets, or evaluation standards used to assess performance.
- **Applicable Chapters**: Ch.5 Evaluation, Ch.6 Results
- **Example (RU)**: "Оценка качества проводится на датасете MS MARCO, широко признанном эталоне для задач вопросно-ответных систем [Nguyen et al., 2016]."

---

## 7. validation_standard

- **Definition**: References accepted validation protocols, statistical methods, or quality criteria for research rigor.
- **Applicable Chapters**: Ch.3 Methodology, Ch.5 Evaluation
- **Example (RU)**: "Статистическая значимость результатов проверяется с помощью t-теста Стьюдента при уровне значимости p < 0.05 [Cohen, 1988]."

---

## 8. empirical_support

- **Definition**: Cites empirical findings from prior studies that directly support or corroborate the thesis claims.
- **Applicable Chapters**: Ch.2 Literature Review, Ch.6 Results, Ch.7 Discussion
- **Example (RU)**: "Эксперименты подтверждают, что цепочка рассуждений (chain-of-thought) повышает качество ответов LLM на сложных задачах [Wei et al., 2022]."

---

## 9. contradiction

- **Definition**: References findings or arguments that contradict, challenge, or present alternative views to the thesis position — used to acknowledge and address counterarguments.
- **Applicable Chapters**: Ch.2 Literature Review, Ch.7 Discussion
- **Example (RU)**: "Однако другие авторы утверждают, что увеличение размера модели не всегда приводит к улучшению качества [Author, Year]."

---

## 10. contribution_positioning

- **Definition**: Frames the thesis contribution relative to existing work, showing novelty, extension, or differentiation.
- **Applicable Chapters**: Ch.1 Introduction, Ch.7 Discussion, Ch.8 Conclusion
- **Example (RU)**: "В отличие от работы [Author, Year], которая ограничивается текстовыми документами, предлагаемый подход поддерживает мультимодальные источники."

---

## 11. structure_reference

- **Definition**: References foundational theoretical frameworks, models, or organizational structures that the thesis builds upon or adapts.
- **Applicable Chapters**: Ch.2 Literature Review, Ch.3 Methodology, Ch.4 System Architecture
- **Example (RU)**: "Архитектура системы основана на принципах модульности, описанных в [Bass et al., 2012]."

---

## 12. supplementary_detail

- **Definition**: Provides additional technical or contextual detail that enriches understanding but is not central to the main argument.
- **Applicable Chapters**: Any chapter (appendices, footnotes)
- **Example (RU)**: "Подробное описание параметров обучения модели приведено в [Author, Year, Appendix A]."

---

## Summary Table

| # | Role | Primary Function | Typical Chapters |
|---|------|-----------------|-----------------|
| 1 | background_context | Orient the reader | Ch.1, Ch.2, Ch.7 |
| 2 | research_gap | Justify the study | Ch.1, Ch.2 |
| 3 | definition | Define key terms | Ch.1, Ch.3, Ch.4 |
| 4 | method_basis | Source of method | Ch.3, Ch.4, Ch.5 |
| 5 | method_comparison | Justify method choice | Ch.3, Ch.7 |
| 6 | benchmark | Evaluation dataset/standard | Ch.5, Ch.6 |
| 7 | validation_standard | Rigor protocol | Ch.3, Ch.5 |
| 8 | empirical_support | Corroborate claims | Ch.2, Ch.6, Ch.7 |
| 9 | contradiction | Address counterarguments | Ch.2, Ch.7 |
| 10 | contribution_positioning | Show novelty | Ch.1, Ch.7, Ch.8 |
| 11 | structure_reference | Theoretical foundation | Ch.2, Ch.3, Ch.4 |
| 12 | supplementary_detail | Enrich with detail | Any |
