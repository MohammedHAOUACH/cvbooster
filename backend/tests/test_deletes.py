"""Delete endpoints must actually delete DB rows (and cascade)."""
import os

from conftest import make_user
from src.services import sqlite_storage


def _seed(client, headers, user_id):
    orig = sqlite_storage.storage.insert_original_cv({
        "user_id": user_id, "file_url": "/api/files/original-cvs/del-orig.pdf",
        "file_name": "del-orig.pdf", "file_size": 1, "extracted_data": {},
    })
    with open(os.path.join(os.environ["UPLOADS_DIR"], "original-cvs", "del-orig.pdf"), "wb") as f:
        f.write(b"%PDF-1.4")
    job = sqlite_storage.storage.insert_job_posting({
        "user_id": user_id, "raw_content": "job", "detected_language": "en",
    })
    gen = sqlite_storage.storage.insert_generated_cv({
        "user_id": user_id, "original_cv_id": orig["id"], "job_posting_id": job["id"],
        "template_name": "clean", "file_url": "/api/files/generated-cvs/del-gen.pdf",
        "llm_output": {},
    })
    with open(os.path.join(os.environ["UPLOADS_DIR"], "generated-cvs", "del-gen.pdf"), "wb") as f:
        f.write(b"%PDF-1.4")
    return orig, job, gen


def test_delete_job_removes_row_and_cascades(client):
    user_id, headers = make_user()
    orig, job, gen = _seed(client, headers, user_id)

    r = client.delete(f"/api/jobs/{job['id']}", headers=headers)
    assert r.status_code == 200

    # job row gone
    assert sqlite_storage.storage.get_job_posting(job["id"]) is None
    # generated CV cascaded (row + file)
    assert sqlite_storage.storage.get_generated_cv(gen["id"]) is None
    assert not os.path.exists(os.path.join(os.environ["UPLOADS_DIR"], "generated-cvs", "del-gen.pdf"))
    # original CV untouched
    assert sqlite_storage.storage.get_original_cv(orig["id"]) is not None


def test_delete_original_cv_removes_row_and_cascades(client):
    user_id, headers = make_user()
    orig, job, gen = _seed(client, headers, user_id)

    r = client.delete(f"/api/upload/cv/{orig['id']}", headers=headers)
    assert r.status_code == 200

    assert sqlite_storage.storage.get_original_cv(orig["id"]) is None
    assert sqlite_storage.storage.get_generated_cv(gen["id"]) is None
    assert not os.path.exists(os.path.join(os.environ["UPLOADS_DIR"], "original-cvs", "del-orig.pdf"))
    # job posting untouched
    assert sqlite_storage.storage.get_job_posting(job["id"]) is not None


def test_delete_only_own_records(client):
    user_id, headers = make_user()
    _, intruder_headers = make_user("intruder")
    orig, job, _ = _seed(client, headers, user_id)

    r = client.delete(f"/api/upload/cv/{orig['id']}", headers=intruder_headers)
    assert r.status_code == 404
    r = client.delete(f"/api/jobs/{job['id']}", headers=intruder_headers)
    assert r.status_code == 404
