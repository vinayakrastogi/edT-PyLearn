import pytest
from fastapi import HTTPException

from app.api.generate import _assert_public_url, _slug
from app.content_repository.file_repo import _check_id


@pytest.mark.parametrize("bad", ["../etc", "a/b", "..", "", "a b", "a\\b"])
def test_ids_that_could_escape_content_dir_are_rejected(bad):
    with pytest.raises(HTTPException):
        _check_id(bad)


def test_normal_ids_pass():
    assert _check_id("module-1-introduction-to-python") == "module-1-introduction-to-python"


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/admin", "http://localhost:8000", "http://169.254.169.254/latest/meta-data",
    "http://10.0.0.5/", "file:///etc/passwd", "ftp://example.com",
])
def test_ssrf_urls_are_blocked(url):
    with pytest.raises(HTTPException):
        _assert_public_url(url)


def test_slug_strips_path_characters():
    assert "/" not in _slug("../../evil", "x")
    assert _slug("", "fallback") == "fallback"


@pytest.mark.parametrize("url,expected", [
    ("postgresql://user:password@localhost/db", "postgresql+psycopg2://user:password@localhost/db"),
    ("sqlite://", "sqlite://"),
])
def test_database_url_uses_the_installed_driver(url, expected):
    from app.core.config import Settings
    assert Settings(_env_file=None, DATABASE_URL=url).DATABASE_URL == expected
