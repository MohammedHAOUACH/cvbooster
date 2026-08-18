"""Upload validation, sanitization and detected_style persistence."""
import io
import os

import pytest

from conftest import make_user
import src.routers.upload as upload_router

PDF_HEADER = b"%PDF-1.4\nfake pdf body\n%%EOF"


def _upload(client, headers, content, filename="my cv (2024)!.pdf"):
    return client.post(
        "/api/upload/cv",
        files={"file": (filename, io.BytesIO(content), "application/pdf")},
        headers=headers,
    )


def test_rejects_non_pdf_magic_bytes(client, monkeypatch):
    monkeypatch.setattr(upload_router, "parse_cv_pdf", lambda b: {"detected_style": "clean"})
    _, headers = make_user()
    r = _upload(client, headers, b"hello, this is not a pdf")
    assert r.status_code == 400


def test_rejects_wrong_content_type(client):
    _, headers = make_user()
    r = client.post(
        "/api/upload/cv",
        files={"file": ("a.txt", io.BytesIO(b"data"), "text/plain")},
        headers=headers,
    )
    assert r.status_code == 400


def test_detected_style_is_persisted(client, monkeypatch):
    """The style computed by the parser must be stored on the record."""
    monkeypatch.setattr(
        upload_router,
        "parse_cv_pdf",
        lambda b: {"raw_text": "x", "personal_info": {}, "sections": [], "detected_style": "tech"},
    )
    _, headers = make_user()
    r = _upload(client, headers, PDF_HEADER)
    assert r.status_code == 200, r.text
    cv = r.json()["cv"]
    assert cv["detected_style"] == "tech"


def test_filename_sanitized(client, monkeypatch):
    monkeypatch.setattr(upload_router, "parse_cv_pdf", lambda b: {"detected_style": "clean"})
    _, headers = make_user()
    r = _upload(client, headers, PDF_HEADER, filename="../../etc/evil.pdf")
    assert r.status_code == 200, r.text
    cv = r.json()["cv"]
    # no path separators in the stored file name / url
    assert "/" not in os.path.basename(cv["file_url"])
    assert ".." not in os.path.basename(cv["file_url"])
    assert os.path.basename(cv["file_url"]) in os.listdir(os.environ["UPLOADS_DIR"] + "/original-cvs")
