"""Tests for PhD Thesis Butler asset files and directory structure."""
import re
from pathlib import Path


def test_build_info_exists(project_root):
    """BUILD_INFO.json must exist at project root."""
    assert (project_root / "BUILD_INFO.json").is_file()


def test_skill_md_version_consistency(project_root):
    """SKILL.md front-matter must declare name=phd-thesis-butler-polish, version=3.0."""
    skill_md = project_root / "SKILL.md"
    assert skill_md.is_file(), "SKILL.md not found"
    text = skill_md.read_text(encoding="utf-8")

    # Extract YAML front-matter
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, "SKILL.md has no YAML front-matter"
    fm = match.group(1)

    name_match = re.search(r'name:\s*"?([\w-]+)"?', fm)
    assert name_match, "name field not found in SKILL.md front-matter"
    assert name_match.group(1) == "phd-thesis-butler"

    ver_match = re.search(r'version:\s*"?([\d.]+)"?', fm)
    assert ver_match, "version field not found in SKILL.md front-matter"
    assert ver_match.group(1) == "3.3.5"


def test_asset_dirs_exist(project_root):
    """Three core asset directories must exist: global, cluster, discipline."""
    assets = project_root / "assets"
    for subdir in ("global", "cluster", "discipline"):
        assert (assets / subdir).is_dir(), f"assets/{subdir} missing"


def test_cluster_subdirs_exist(project_root):
    """Cluster directory must contain expected sub-cluster dirs."""
    cluster = project_root / "assets" / "cluster"
    expected = {"GLOBAL", "TECH_LIFE", "HUM_SOC"}
    actual = {p.name for p in cluster.iterdir() if p.is_dir()}
    missing = expected - actual
    assert not missing, f"Missing cluster subdirs: {missing}"


def test_global_master_has_files(project_root):
    """assets/global/master/ must contain at least one .jsonl file."""
    master_dir = project_root / "assets" / "global" / "master"
    jsonl_files = list(master_dir.glob("*.jsonl"))
    assert len(jsonl_files) > 0, "No .jsonl files in assets/global/master/"


def test_global_quality_has_files(project_root):
    """assets/global/quality/ must contain at least one .jsonl file."""
    quality_dir = project_root / "assets" / "global" / "quality"
    jsonl_files = list(quality_dir.glob("*.jsonl"))
    assert len(jsonl_files) > 0, "No .jsonl files in assets/global/quality/"


def test_discipline_subject_count(build_info):
    """BUILD_INFO should report 34 discipline subjects."""
    assert build_info["layers"]["DISCIPLINE_subjects"] == 34
