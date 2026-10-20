import os
import shutil
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Every test session works on a throw-away copy of data/ and without any LLM.
_TMP = tempfile.mkdtemp(prefix="code-hinter-tests-")
for name in ("exercises.json", "profs.json", "students.json", "stud_prof.json", "stud_exe.json"):
    shutil.copy(os.path.join(ROOT, "data", name), _TMP)
os.environ["CH_DATA_DIR"] = _TMP
os.environ["CH_LLM_BACKEND"] = "offline"

import main  # noqa: E402  (must come after the environment is set)

@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    return main.app.test_client()

@pytest.fixture
def student():
    """Seed student #1 (benalla@example.com, professor 1, exercises 1 and 2)."""
    return {"email": "benalla@example.com", "id": 1}

@pytest.fixture
def fresh_student(client):
    """A brand-new student of professor 2 for tests that need a clean learner model."""
    from crud import student_crud, stud_prof_crud
    import uuid
    s = student_crud.create_student({"name": "Test Student", "password": "pass", "email": f"t-{uuid.uuid4().hex[:8]}@example.com"})
    stud_prof_crud.create_stud_prof({"student_id": s["id"], "prof_id": 2})
    return s
