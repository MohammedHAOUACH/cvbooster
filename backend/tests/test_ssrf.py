"""Scrape endpoint must refuse internal/private URLs (SSRF)."""
import pytest

import src.routers.scraper as scraper_router


def _boom(url):
    raise AssertionError(f"scrape_job_url must not be called for {url}")


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:8000/health",
    "http://localhost:3000/",
    "http://169.254.169.254/latest/meta-data/",
    "http://192.168.1.1/",
    "http://10.0.0.5/admin",
    "http://172.16.0.1:5432/",
    "file:///etc/passwd",
    "ftp://example.com/x",
    "http://[::1]/",
    "",
])
def test_internal_urls_rejected_before_network(client, monkeypatch, url):
    monkeypatch.setattr(scraper_router, "scrape_job_url", _boom)
    from conftest import make_user
    _, headers = make_user()
    r = client.post("/api/jobs/scrape", json={"source_url": url}, headers=headers)
    assert r.status_code == 400, (url, r.status_code, r.text)


def test_public_url_allowed_past_guard(client, monkeypatch):
    """A public URL passes the guard and reaches the scraper (mocked)."""
    calls = {}

    async def fake_scrape(url):
        calls["url"] = url
        return {"title": "T", "company": "C", "raw_content": "hello world job", "parsed_data": {}}

    monkeypatch.setattr(scraper_router, "scrape_job_url", fake_scrape)
    from conftest import make_user
    _, headers = make_user()
    r = client.post("/api/jobs/scrape", json={"source_url": "http://example.com/jobs/1"}, headers=headers)
    assert r.status_code == 200, r.text
    assert calls["url"] == "http://example.com/jobs/1"
