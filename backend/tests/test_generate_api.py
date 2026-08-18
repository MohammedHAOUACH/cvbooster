"""CV generation API: template validation + retemplate endpoint."""
import os

import pytest

import src.routers.cv_engine as cv_engine
from conftest import make_user
from src.services import sqlite_storage


@pytest.fixture()
def seeded(client):
    user_id, headers = make_user()
    orig = sqlite_storage.storage.insert_original_cv({
        "user_id": user_id, "file_url": "/api/files/original-cvs/g1.pdf",
        "file_name": "g1.pdf", "file_size": 1, "extracted_data": {}, "detected_style": "clean",
    })
    job = sqlite_storage.storage.insert_job_posting({
        "user_id": user_id, "raw_content": "python sql docker", "detected_language": "en",
    })
    return user_id, headers, orig, job


async def _fake_llm(original_cv_data, job_posting_data, output_language="en"):
    return {
        "basics": {"name": "N", "summary": "s"},
        "skills": [{"name": "S", "keywords": ["python"]}],
    }


def test_unknown_template_rejected(client, seeded, monkeypatch):
    monkeypatch.setattr(cv_engine, "optimize_cv_for_job", _fake_llm)
    _, headers, orig, job = seeded
    r = client.post("/api/cv/generate", json={
        "original_cv_id": orig["id"], "job_posting_id": job["id"], "template_name": "nope",
    }, headers=headers)
    assert r.status_code == 400


def test_generate_and_retemplate(client, seeded, monkeypatch):
    monkeypatch.setattr(cv_engine, "optimize_cv_for_job", _fake_llm)
    _, headers, orig, job = seeded

    r = client.post("/api/cv/generate", json={
        "original_cv_id": orig["id"], "job_posting_id": job["id"], "template_name": "modern",
    }, headers=headers)
    assert r.status_code == 200, r.text
    gen = r.json()["generated_cv"]
    assert os.path.isfile(os.path.join(os.environ["UPLOADS_DIR"], "generated-cvs",
                                       os.path.basename(gen["file_url"])))

    # renamed endpoint /retemplate (old /retail is gone)
    r2 = client.post(f"/api/cv/{gen['id']}/retemplate", json={"template_name": "tech"}, headers=headers)
    assert r2.status_code == 200, r2.text
    assert r2.json()["generated_cv"]["template_name"] == "tech"

    r3 = client.post(f"/api/cv/{gen['id']}/retail", json={"template_name": "tech"}, headers=headers)
    assert r3.status_code == 404
