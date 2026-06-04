# Chapter Evidence Map Template

## Overview

This template produces a structured evidence map that binds each section/subsection
of a thesis chapter to supporting literature. It helps the author identify which
claims are well-supported, partially supported, or lacking evidence.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `chapter_outline` | Markdown | Chapter outline with numbered sections and key claims |
| `literature_records` | JSON array | Normalized literature records from `normalized_literature_sample.json` |
| `chapter_id` | string | Chapter identifier (e.g., `CH2`, `CH3`) |
| `scope` | string | One of: `INTRO`, `METHOD`, `EXPERIMENT`, `CONCLUSION` |

## Output

A JSON object with the following structure:

```json
{
  "chapter_id": "CH2",
  "scope": "METHOD",
  "generated_at": "ISO-8601 timestamp",
  "sections": [
    {
      "section_id": "2.3",
      "section_title": "...",
      "claim": "Key claim or topic of this section",
      "evidence_bindings": [
        {
          "source_id": "normalized_record_id",
          "evidence_role": "background_context | method_basis | empirical_support | method_comparison",
          "coverage": "covered | partial | missing",
          "note": "How this source supports the claim"
        }
      ],
      "coverage_summary": "covered | partial | missing",
      "gap_note": "If partial or missing, describe what evidence is needed"
    }
  ],
  "overall_coverage": "covered | partial | missing",
  "recommendations": [
    "Actionable suggestion to improve evidence coverage"
  ]
}
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `source_id` | Yes | Must match an ID from the normalized literature records. **Never fabricate.** |
| `evidence_role` | Yes | How the source contributes: background_context, method_basis, empirical_support, method_comparison, research_gap |
| `coverage` | Yes | `covered` = claim fully supported; `partial` = some aspects missing; `missing` = no supporting evidence found |
| `gap_note` | Conditional | Required when coverage is `partial` or `missing` |
| `risk_level` | Optional | `low` / `medium` / `high` — reflects how critical the gap is |

## Example

See: `../examples/chapter_evidence_map_sample.json`

### Scenario: Vehicle State Estimation Chapter

Given an outline section "2.4 Extended Kalman Filter for Drivetrain State Estimation":

- `covered`: A literature record with `evidence_role: "method_basis"` describing
  EKF application to gear mesh vibration signals provides direct method_basis support.
- `partial`: Only UKF-based approaches are in the literature; no EKF-specific drivetrain
  application found — `gap_note: "Need EKF-specific drivetrain application or cite general EKF reference + note adaptation"`.
- `missing`: No literature on real-time implementation constraints — `gap_note: "Search for embedded implementation or real-time diagnostics papers"`.

## Usage Notes

1. Every `source_id` MUST exist in the provided `literature_records`. Do not invent IDs.
2. If no suitable source exists for a section, set `coverage: "missing"` and provide
   a `gap_note` suggesting search directions.
3. The template is designed to be consumed by automated polishing pipelines and
   manual review workflows alike.
