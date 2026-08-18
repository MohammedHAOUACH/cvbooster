"""File serving requires authentication and ownership."""
import os

from conftest import make_user
from src.services import sqlite_storage

UPLOADS_DIR = os.environ["UPLOADS_DIR"]
ORIG_DIR = os.path.join(UPLOADS_DIR, "original-cvs")
GEN_DIR = os.path.join(UPLOADS_DIR, "generated-cvs")


def _insert_original_cv(user_id, file_name):
    path = os.path.join(ORIG_DIR, file_name)
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4 test")
    return sqlite_storage.storage.insert_original_cv({
        "user_id": user_id,
        "file_url": f"/api/files/original-cvs/{file_name}",
        "file_name": file_name,
        "file_size": 12,
        "extracted_data": {},
        "detected_style": "clean",
    })


def test_unauthenticated_file_request_401(client):
    _insert_original_cv("owner-1", "orig-1.pdf")
    r = client.get("/api/files/original-cvs/orig-1.pdf")
    assert r.status_code == 401


def test_owner_can_download(client):
    _insert_original_cv("owner-1", "orig-2.pdf")
    _, headers = make_user("owner-1")
    r = client.get("/api/files/original-cvs/orig-2.pdf", headers=headers)
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF")


def test_other_user_cannot_download(client):
    _insert_original_cv("owner-1", "orig-3.pdf")
    _, headers = make_user("intruder")
    r = client.get("/api/files/original-cvs/orig-3.pdf", headers=headers)
    assert r.status_code == 404


def test_generated_cv_unauthenticated_401(client):
    _, h1 = make_user("owner-1")
    from src.services.sqlite_storage import storage
    cv = storage.insert_original_cv({
        "user_id": "owner-1", "file_url": "/api/files/original-cvs/x.pdf",
        "file_name": "x.pdf", "file_size": 1, "extracted_data": {},
    })
    gen = storage.insert_generated_cv({
        "user_id": "owner-1", "original_cv_id": cv["id"],
        "job_posting_id": "j-1", "template_name": "clean",
        "file_url": "/api/files/generated-cvs/gen-1.pdf", "llm_output": {},
    })
    with open(os.path.join(GEN_DIR, "gen-1.pdf"), "wb") as f:
        f.write(b"%PDF-1.4 test")
    r = client.get("/api/files/generated-cvs/gen-1.pdf")
    assert r.status_code == 401
    r = client.get("/api/files/generated-cvs/gen-1.pdf", headers=h1)
    assert r.status_code == 200
