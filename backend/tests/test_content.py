"""Every shipped module must pass the content validator (lessons run, quizzes valid, solutions pass)."""
import pytest

from tools.check_content import CONTENT_DIR, check_module

MODULES = sorted(d for d in CONTENT_DIR.iterdir() if d.is_dir() and (d / "module.yaml").exists())


@pytest.mark.parametrize("module_dir", MODULES, ids=lambda d: d.name)
def test_module_is_valid(module_dir):
    errors = check_module(module_dir)
    assert not errors, "\n".join(errors)
