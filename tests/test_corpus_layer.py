"""Tests for PhD Thesis Butler v4.0 corpus layer schemas and structure."""
import json
from pathlib import Path


def test_workflow_md_exists(project_root):
    """corpus_layer/WORKFLOW.md must exist and have content."""
    path = project_root / "corpus_layer" / "WORKFLOW.md"
    assert path.is_file(), f"WORKFLOW.md not found at {path}"
    content = path.read_text(encoding="utf-8").strip()
    assert len(content) > 50, f"WORKFLOW.md has only {len(content)} chars"


def test_schema_convention_md_exists(project_root):
    """corpus_layer/schemas/SCHEMA_CONVENTION.md must exist."""
    path = project_root / "corpus_layer" / "schemas" / "SCHEMA_CONVENTION.md"
    assert path.is_file(), f"SCHEMA_CONVENTION.md not found at {path}"


def test_all_schema_files_exist(project_root):
    """All 5 schema files must exist in corpus_layer/schemas/."""
    schemas_dir = project_root / "corpus_layer" / "schemas"
    expected = [
        "paper_record.schema.json",
        "structure_record.schema.json",
        "rhetorical_move.schema.json",
        "methodology_record.schema.json",
        "logic_chain.schema.json",
    ]
    for name in expected:
        path = schemas_dir / name
        assert path.is_file(), f"Missing schema: {name}"


def test_all_schemas_parse_as_json(project_root):
    """All schema files must parse as valid JSON objects."""
    schemas_dir = project_root / "corpus_layer" / "schemas"
    schema_files = list(schemas_dir.glob("*.schema.json"))
    assert len(schema_files) >= 5, f"Expected at least 5 schemas, found {len(schema_files)}"

    for sf in schema_files:
        with open(sf, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), f"{sf.name} did not parse as a JSON object"


def test_each_schema_has_evidence_count(project_root):
    """Every schema must define an evidence_count field in its properties."""
    schemas_dir = project_root / "corpus_layer" / "schemas"
    schema_files = list(schemas_dir.glob("*.schema.json"))
    assert len(schema_files) >= 5

    for sf in schema_files:
        with open(sf, encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        assert "evidence_count" in props, (
            f"{sf.name}: missing 'evidence_count' in properties"
        )
        ec = props["evidence_count"]
        assert ec.get("type") == "object", (
            f"{sf.name}: evidence_count.type should be 'object', got {ec.get('type')}"
        )
        ec_props = ec.get("properties", {})
        for required_field in ("count", "source", "confidence"):
            assert required_field in ec_props, (
                f"{sf.name}: evidence_count missing '{required_field}' sub-field"
            )


def test_schema_id_patterns(project_root):
    """Schema ID fields must have correct patterns (paper_, structure_, move_, etc.)."""
    schemas_dir = project_root / "corpus_layer" / "schemas"

    expected_ids = {
        "paper_record.schema.json": ("id", r"^paper_[0-9]{4,}$"),
        "structure_record.schema.json": ("id", r"^structure_[0-9]{4,}$"),
        "rhetorical_move.schema.json": ("move_id", r"^move_[0-9]{4,}$"),
        "methodology_record.schema.json": ("methodology_id", r"^methodology_[0-9]{4,}$"),
        "logic_chain.schema.json": ("chain_id", r"^chain_[0-9]{4,}$"),
    }

    for schema_name, (id_field, expected_pattern) in expected_ids.items():
        path = schemas_dir / schema_name
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        assert id_field in props, f"{schema_name}: missing '{id_field}' field"
        actual_pattern = props[id_field].get("pattern")
        assert actual_pattern == expected_pattern, (
            f"{schema_name}.{id_field}.pattern: "
            f"expected {expected_pattern!r}, got {actual_pattern!r}"
        )


def test_schema_version_4(project_root):
    """All schema files must declare version 4.0."""
    schemas_dir = project_root / "corpus_layer" / "schemas"
    for sf in sorted(schemas_dir.glob("*.schema.json")):
        with open(sf, encoding="utf-8") as f:
            schema = json.load(f)
        version = schema.get("version")
        assert version == "4.0", (
            f"{sf.name}: expected version '4.0', got {version!r}"
        )


def test_discipline_enum_in_schemas(project_root):
    """Schemas using cluster field must include valid enum values."""
    schemas_dir = project_root / "corpus_layer" / "schemas"
    valid_clusters = {"TECH_LIFE", "HUM_SOC", "ART_SPORT", "MATH_PHYS", "GLOBAL"}

    for sf in sorted(schemas_dir.glob("*.schema.json")):
        with open(sf, encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        if "cluster" in props:
            cluster_enum = set(props["cluster"].get("enum", []))
            assert cluster_enum == valid_clusters, (
                f"{sf.name}: cluster enum {cluster_enum} != {valid_clusters}"
            )
