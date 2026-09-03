import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import workspace as ws  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "basic-001-muon-scintillator"


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_baseline_has_only_task_md(self):
        dest = ws.create_workspace(BENCHMARK_DIR, "baseline", REPO_ROOT, self.tmp / "ws")
        contents = sorted(p.name for p in dest.iterdir())
        self.assertEqual(contents, ["task.md"])

    def test_treatment_includes_skills_and_knowledge(self):
        dest = ws.create_workspace(BENCHMARK_DIR, "treatment", REPO_ROOT, self.tmp / "ws")
        self.assertTrue((dest / "task.md").exists())
        self.assertTrue((dest / "llm4geant4" / "skills" / "llm4geant4" / "SKILL.md").exists())
        self.assertTrue((dest / "llm4geant4" / "knowledge" / "geometry.md").exists())

    def test_forbidden_files_never_present(self):
        for condition in ("baseline", "treatment"):
            dest = ws.create_workspace(BENCHMARK_DIR, condition, REPO_ROOT, self.tmp / f"ws-{condition}")
            names = {p.name for p in dest.rglob("*")}
            self.assertFalse(names & ws.FORBIDDEN_NAMES, f"forbidden content leaked into {condition} workspace")

    def test_rejects_unknown_condition(self):
        with self.assertRaises(ValueError):
            ws.create_workspace(BENCHMARK_DIR, "nonsense", REPO_ROOT, self.tmp / "ws")


if __name__ == "__main__":
    unittest.main()
