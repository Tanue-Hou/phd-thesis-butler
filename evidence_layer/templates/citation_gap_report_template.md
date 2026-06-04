# Citation Gap Report Template

## Overview

This template analyzes a user-provided paragraph sentence by sentence and reports
citation gaps — sentences that make claims without adequate literature support.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `paragraph` | string | A paragraph of academic text (any language) |
| `literature_records` | JSON array | Normalized literature records |
| `language` | string | ISO language code (e.g., `ru`, `en`, `zh`) |
| `discipline` | string | Academic discipline context |

## Output

A JSON object:

```json
{
  "paragraph_id": "auto-generated",
  "analyzed_at": "ISO-8601 timestamp",
  "language": "ru",
  "sentences": [
    {
      "sentence_id": 1,
      "text": "Original sentence text",
      "claim_type": "factual | method_basis | interpretive | descriptive",
      "requires_citation": true,
      "coverage": "covered | partial | missing",
      "matched_sources": [
        {
          "source_id": "record_id",
          "relevance": "direct | indirect",
          "note": "How the source relates to the sentence"
        }
      ],
      "risk_level": "low | medium | high",
      "suggestion": "What action to take"
    }
  ],
  "summary": {
    "total_sentences": 5,
    "covered": 2,
    "partial": 1,
    "missing": 2,
    "high_risk_count": 2
  },
  "recommendations": [
    "Prioritized list of actions to close citation gaps"
  ]
}
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `claim_type` | Yes | `factual` = stating a fact/study result; `method_basis` = describing a method; `interpretive` = author's analysis/opinion; `descriptive` = background/context |
| `requires_citation` | Yes | `true` for factual/method_basis claims; may be `false` for descriptive sentences that are common knowledge |
| `coverage` | Yes | `covered` = matched source exists; `partial` = source exists but doesn't fully support the claim; `missing` = no source found |
| `risk_level` | Yes | `high` = factual/method_basis claim with no citation (academic integrity risk); `medium` = partial coverage; `low` = covered or common knowledge |
| `suggestion` | Yes | Actionable advice: cite specific source, search for evidence, rephrase as opinion, mark as common knowledge |

## Example

See: `../examples/citation_gap_report_sample.json`

### Scenario

Sentence: "ЭКФ широко применяется для оценки состояния трансмиссии"
(EKF is widely used for drivetrain state estimation)

- `claim_type`: "factual"
- `requires_citation`: true
- `coverage`: "partial" — EKF usage papers exist but none specifically for drivetrain
- `risk_level`: "high"
- `suggestion`: "Cite general EKF diagnostic application + note gap for drivetrain-specific use, or rephrase to 'has been applied in some diagnostic contexts'"

## Usage Notes

1. Sentences that are purely transitional or definitional (common knowledge) can
   be marked `requires_citation: false` with `risk_level: "low"`.
2. Never fabricate a `source_id`. If no match exists, use `coverage: "missing"`.
3. This report feeds into the polishing pipeline — high-risk items are flagged
   for the user before any automated rewriting.
