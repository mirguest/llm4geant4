import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.report import render_markdown  # noqa: E402


def _write_run(results_dir: Path, run_id: str, *, agent: str, model: str, condition: str,
                automated_score: float, automated_max: float, exit_code: int = 0, manual: bool = False) -> None:
    run_dir = results_dir / run_id
    run_dir.mkdir(parents=True)
    manifest = {
        "run_id": run_id, "benchmark": "basic-001-muon-scintillator", "agent": agent,
        "model": model, "condition": condition, "trial": "1", "exit_code": exit_code,
        "timed_out": False, "duration_seconds": 1.0,
    }
    score = {
        "benchmark": "basic-001-muon-scintillator", "criteria": {}, "automated_score": automated_score,
        "automated_max": automated_max, "total_max": 100, "needs_manual_review": manual,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "score.json").write_text(json.dumps(score))


class TestReport(unittest.TestCase):
    def setUp(self):
        self.results_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.results_dir, ignore_errors=True)

    def test_empty_results_dir(self):
        report = render_markdown(self.results_dir)
        self.assertIn("No completed runs", report)

    def test_report_includes_agent_model_and_delta(self):
        _write_run(self.results_dir, "run-baseline", agent="claude-code", model="claude-sonnet-5",
                   condition="baseline", automated_score=40, automated_max=65)
        _write_run(self.results_dir, "run-treatment", agent="claude-code", model="claude-sonnet-5",
                   condition="treatment", automated_score=55, automated_max=65)

        report = render_markdown(self.results_dir)
        self.assertIn("claude-code", report)
        self.assertIn("claude-sonnet-5", report)
        self.assertIn("baseline", report)
        self.assertIn("treatment", report)
        self.assertIn("+15.0", report)

    def test_ignores_incomplete_runs(self):
        run_dir = self.results_dir / "incomplete"
        run_dir.mkdir()
        (run_dir / "manifest.json").write_text("{}")
        # no score.json written
        report = render_markdown(self.results_dir)
        self.assertIn("No completed runs", report)


if __name__ == "__main__":
    unittest.main()
