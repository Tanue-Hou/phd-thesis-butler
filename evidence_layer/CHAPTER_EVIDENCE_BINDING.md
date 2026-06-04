# Chapter-Evidence Binding Rules

> Version: 1.0 | Predefined role→chapter mappings and binding rules

---

## Role-Chapter Mapping Matrix

The table below shows which evidence roles are expected (✓), optional (○), or not applicable (—) for each chapter type.

| Evidence Role | Ch.1 Intro | Ch.2 Lit.Review | Ch.3 Method | Ch.4 Architecture | Ch.5 Eval | Ch.6 Results | Ch.7 Discussion | Ch.8 Conclusion |
|---|---|---|---|---|---|---|---|---|
| background_context | ✓ | ✓ | ○ | — | — | — | ✓ | ○ |
| research_gap | ✓ | ✓ | ○ | — | — | — | ○ | ○ |
| definition | ✓ | ○ | ✓ | ✓ | — | — | ○ | — |
| method_basis | — | ○ | ✓ | ✓ | — | — | ○ | — |
| method_comparison | — | ○ | ✓ | — | — | — | ✓ | — |
| benchmark | — | — | ○ | — | ✓ | ✓ | ○ | — |
| validation_standard | — | — | ✓ | — | ✓ | — | ○ | — |
| empirical_support | — | ✓ | — | — | — | ✓ | ✓ | ○ |
| contradiction | — | ✓ | — | — | — | — | ✓ | — |
| contribution_positioning | ✓ | — | — | — | — | — | ✓ | ✓ |
| structure_reference | — | ✓ | ○ | ✓ | — | — | ○ | — |
| supplementary_detail | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

**Legend**: ✓ = Expected | ○ = Optional | — = Not applicable

---

## Binding Rules

### Rule 1: Minimum Coverage Per Chapter

Every chapter MUST have bindings for its ✓-marked roles before it can pass gap analysis.

```
IF role is ✓ for chapter AND no binding exists → gap_status = missing
IF role is ○ for chapter AND no binding exists → gap_status = not_needed (acceptable)
IF role is — for chapter → gap_status = not_needed (enforced)
```

### Rule 2: Evidence Strength Threshold

| Chapter Section | Minimum Strength |
|----------------|-----------------|
| Literature Review (Ch.2) | medium |
| Methodology (Ch.3) | strong |
| Results (Ch.6) | strong |
| Introduction (Ch.1) | weak (acceptable for background) |
| Discussion (Ch.7) | medium |

```
IF evidence_strength < threshold → gap_status = partial
IF evidence_strength ≥ threshold → gap_status = covered
```

### Rule 3: Role Consistency

A single source can serve multiple roles, but each binding record specifies exactly one role per claim. If a source supports a claim in two different ways, create two separate binding records.

### Rule 4: Chapter-Specific Mandatory Roles

These roles MUST appear at least once per chapter:

- **Ch.1 Introduction**: background_context, research_gap, contribution_positioning
- **Ch.2 Literature Review**: background_context, research_gap, empirical_support
- **Ch.3 Methodology**: definition, method_basis, validation_standard
- **Ch.4 Architecture**: definition, method_basis, structure_reference
- **Ch.5 Evaluation**: benchmark, validation_standard
- **Ch.6 Results**: benchmark, empirical_support
- **Ch.7 Discussion**: background_context, empirical_support, contradiction, contribution_positioning
- **Ch.8 Conclusion**: contribution_positioning

### Rule 5: Cross-Chapter Consistency

Sources cited in multiple chapters must maintain consistent metadata. If a source is cited in Ch.2 with role `empirical_support` and in Ch.7 with role `contradiction`, both bindings are valid but must reference the same source_id.

### Rule 6: Contradiction Handling

When role = `contradiction`:
- The binding must include a `rebuttal_note` field explaining how the contradiction is addressed
- At least one additional binding with role `empirical_support` or `method_comparison` should accompany it

---

## Binding Priority

When multiple roles could apply to a single claim, select the role in this priority order:

1. `research_gap` (highest — justifies the study)
2. `contradiction` (must be explicitly addressed)
3. `method_basis` (methods need authoritative grounding)
4. `validation_standard` (rigor is non-negotiable)
5. `benchmark` (evaluation needs recognized standards)
6. `definition` (terminology must be precise)
7. `empirical_support` (corroboration)
8. `method_comparison` (selection justification)
9. `contribution_positioning` (novelty framing)
10. `structure_reference` (theoretical grounding)
11. `background_context` (general framing)
12. `supplementary_detail` (lowest priority)
