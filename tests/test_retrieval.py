"""Smoke tests for retrieve_templates.py importability."""
import sys
from pathlib import Path


def test_retrieve_templates_importable(project_root):
    """retrieve_templates.py must be importable without errors."""
    scripts_dir = project_root / "scripts"
    # Add scripts dir to sys.path temporarily
    sys.path.insert(0, str(scripts_dir))
    try:
        import retrieve_templates
        assert hasattr(retrieve_templates, "retrieve")
        assert callable(retrieve_templates.retrieve)
    finally:
        sys.path.pop(0)
        # Clean up module cache so it doesn't leak
        sys.modules.pop("retrieve_templates", None)


def test_retrieve_templates_has_base_path(project_root):
    """retrieve_templates.py should resolve BASE to project root."""
    scripts_dir = project_root / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        import retrieve_templates
        assert retrieve_templates.BASE == project_root
    finally:
        sys.path.pop(0)
        sys.modules.pop("retrieve_templates", None)
