# Evidence-Aware Polishing Template

## Overview

This template takes a user-written paragraph (typically in Russian) and produces
a polished version with citation suggestions. It improves academic style while
preserving the author's meaning and flagging evidence gaps.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `paragraph` | string | Original paragraph in Russian (or other language) |
| `available_literature` | JSON array | Normalized literature records available for citation |
| `target_language` | string | Output language code (default: same as input) |
| `style_profile` | string | `academic_formal` (default) or `academic_concise` |
| `discipline` | string | Academic field context |

## Output

A JSON object:

```json
{
  "original": "Original paragraph text",
  "polished": "Polished paragraph text with [source_id] placeholders",
  "language": "ru",
  "changes": [
    {
      "original_fragment": "original phrasing",
      "polished_fragment": "improved phrasing",
      "reason": "grammar | style | precision | clarity",
      "citation_inserted": false
    }
  ],
  "citation_suggestions": [
    {
      "position": "after sentence N or fragment description",
      "source_id": "record_id",
      "confidence": "high | medium | low",
      "reason": "Why this citation is appropriate here"
    }
  ],
  "unresolved_claims": [
    {
      "fragment": "text with no matching evidence",
      "suggestion": "search query or rephrase advice"
    }
  ],
  "integrity_notes": [
    "Any concerns about academic integrity boundaries"
  ]
}
```

## Academic Integrity Boundaries

This template operates under strict integrity rules:

1. **NO FABRICATION**: The template NEVER invents citations, statistics, or
   factual claims. If no source supports a claim, it is flagged as `unresolved`.

2. **NO MEANING CHANGE**: Polishing preserves the author's intended meaning.
   Style and grammar are improved, but substantive content is not altered.

3. **CITATION SUGGESTIONS ONLY**: The `citation_suggestions` array provides
   recommendations. The author must verify and approve every citation before
   inclusion. Citations are marked as `[source_id]` placeholders, NOT formatted
   references.

4. **NO PLAGIARISM**: The polishing does not rewrite others' published text
   into the user's paragraph. It improves the user's own writing.

5. **TRANSPARENCY**: Every change is logged in the `changes` array with a
   reason, so the author can review and reject any modification.

6. **SOURCE VERIFICATION**: Every `source_id` in suggestions must exist in
   `available_literature`. If no match is found, the claim goes into
   `unresolved_claims`.

## Example

See inline usage in the evidence layer pipeline documentation.

### Input (Russian)
"Методы оценки технического состояния трансмиссии основаны на анализе
вибросигналов. Расширенный фильтр Калмана позволяет оценивать параметры
системы в реальном времени."

### Polished (Russian, with placeholders)
"Методы оценки технического состояния трансмиссии основаны на анализе
вибросигналов [VIB_DIAG_001]. Расширенный фильтр Калмана, адаптированный
для задач диагностики, позволяет оценивать параметры системы в реальном
времени [EKF_STATE_001]."

### Citation Suggestions
- Position: after sentence 1 → source_id: VIB_DIAG_001, confidence: high
- Position: after sentence 2 → source_id: EKF_STATE_001, confidence: medium

## Usage Notes

1. Always present `unresolved_claims` to the user — never silently drop them.
2. The author retains full control: all changes are suggestions.
3. For dissertation writing, the author's advisor should review any
   AI-assisted polishing before submission.
