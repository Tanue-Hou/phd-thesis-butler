"""BUILD_INFO.json quality / integrity checks."""
REQUIRED_TOP_KEYS = {
    "project", "version", "release_date", "schema_version",
    "description", "templates", "sources", "layers", "quality",
    "categories", "retrieval",
}


def test_build_info_has_required_keys(build_info):
    """BUILD_INFO must contain all required top-level keys."""
    missing = REQUIRED_TOP_KEYS - set(build_info.keys())
    assert not missing, f"Missing BUILD_INFO keys: {missing}"


def test_build_info_version_format(build_info):
    """Version must be a valid semver-like string."""
    ver = build_info["version"]
    parts = ver.split(".")
    assert len(parts) == 3, f"Expected 3-part version, got: {ver}"
    for p in parts:
        assert p.isdigit(), f"Non-numeric version part: {p}"


def test_build_info_templates_section(build_info):
    """templates section must have DIS, AREF, and total counts."""
    templates = build_info["templates"]
    for key in ("total", "DIS", "AREF", "UTILS"):
        assert key in templates, f"templates.{key} missing"
        assert isinstance(templates[key], int)
        assert templates[key] >= 0


def test_build_info_layers_section(build_info):
    """layers section must define GLOBAL, TECH_LIFE, HUM_SOC."""
    layers = build_info["layers"]
    for key in ("GLOBAL", "TECH_LIFE", "HUM_SOC"):
        assert key in layers, f"layers.{key} missing"
        assert isinstance(layers[key], int)
        assert layers[key] >= 0


def test_build_info_quality_section(build_info):
    """quality section must have Q0, Q1, Q2 counts."""
    quality = build_info["quality"]
    for key in ("Q0", "Q1", "Q2"):
        assert key in quality, f"quality.{key} missing"
        assert isinstance(quality[key], int)
        assert quality[key] >= 0


def test_build_info_sources_nonempty(build_info):
    """sources.total_documents must be positive."""
    assert build_info["sources"]["total_documents"] > 0
