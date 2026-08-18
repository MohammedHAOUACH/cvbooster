"""ATS scoring: honest coverage, French keywords supported."""
from src.services.ats_optimizer import calculate_ats_score, extract_keywords_from_job


def test_french_keywords_extracted():
    job = {"raw_content": "Requis : Python, SQL, Docker, Kubernetes, machine learning, leadership, gestion de projet"}
    kws = extract_keywords_from_job(job)
    all_kw = [k for v in kws.values() for k in v]
    assert "python" in all_kw
    assert "docker" in all_kw
    assert "machine learning" in all_kw


def test_score_is_coverage_not_scaled():
    job = {"raw_content": "We need python and sql."}
    cv = {
        "basics": {"summary": "python"},
        "work": [{"position": "", "company": "", "summary": "", "highlights": ["sql"]}],
        "skills": [{"name": "", "keywords": []}],
    }
    result = calculate_ats_score(cv, job)
    assert result["keywords_total"] == 2
    assert result["keywords_matched"] == 2
    assert result["score"] == 100.0  # straight 100%, no artificial 1.2x scaling


def test_zero_keywords_scores_zero():
    job = {"raw_content": "un texte sans aucun mot-cle connu"}
    cv = {"basics": {"summary": "x"}}
    result = calculate_ats_score(cv, job)
    assert result["score"] == 0.0
    assert result["keywords_total"] == 0
