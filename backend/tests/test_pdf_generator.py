"""PDF generation writes to the requested path and does not mutate input."""
import os

from src.services.pdf_generator import generate_cv_pdf

CV = {
    "basics": {"name": "Test Person", "email": "t@e.st", "summary": "Résumé FR."},
    "work": [{"company": "ACME", "position": "Dev", "startDate": "2020-01",
              "endDate": "Present", "summary": "S.", "highlights": ["h1"]}],
    "skills": [{"name": "Langages", "keywords": ["Python"]}],
}


def test_output_path_respected(tmp_path):
    out = str(tmp_path / "out.pdf")
    result = generate_cv_pdf(CV, "clean", "fr", "clean", out)
    assert result == out
    assert os.path.isfile(out)
    with open(out, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_input_not_mutated():
    import copy
    snapshot = copy.deepcopy(CV)
    out = "/tmp/_cvbooster_test_nofile.pdf"
    try:
        generate_cv_pdf(CV, "clean", "fr", "clean", out)
    finally:
        if os.path.exists(out):
            os.remove(out)
    assert CV == snapshot
