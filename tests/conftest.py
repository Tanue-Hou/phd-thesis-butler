"""Shared fixtures for PhD Thesis Butler test suite."""
import json
import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def build_info(project_root) -> dict:
    """Load and return BUILD_INFO.json contents."""
    path = project_root / "BUILD_INFO.json"
    assert path.exists(), f"BUILD_INFO.json not found at {path}"
    return json.loads(path.read_text(encoding="utf-8"))
