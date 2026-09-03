import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.judge import judge_run, parse_judge_output  # noqa: E402
from lib.pipeline import BENCHMARKS_DIR  # noqa: E402
from lib.scoring import score_workspace  # noqa: E402

BENCHMARK_DIR = BENCHMARKS_DIR / "basic-001-muon-scintillator"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# A fake "judge" that ignores the prompt and just prints canned JSON --
# proves the invoke/parse/merge pipeline without needing a real LLM or
# network access in the test environment.
FAKE_JUDGE_COMMAND = (
    "python3 -c \"import json; print(json.dumps({"
    "'build_and_run': {'score': 12, 'justification': 'looks complete'}, "
    "'output': {'score': 8, 'justification': 'analysis manager present'}, "
    "'physics_plausibility': {'score': 7, 'justification': 'plausible order of magnitude'}"
    "}))\""
)

BROKEN_JUDGE_COMMAND = "python3 -c \"print('not json at all')\""


class TestParseJudgeOutput(unittest.TestCase):
    def test_parses_bare_json(self):
        result = parse_judge_output('{"a": {"score": 1}}')
        self.assertEqual(result, {"a": {"score": 1}})

    def test_parses_json_with_surrounding_prose(self):
        raw = 'Here is my scoring:\n{"a": {"score": 1}}\nHope that helps!'
        result = parse_judge_output(raw)
        self.assertEqual(result, {"a": {"score": 1}})

    def test_raises_on_no_json(self):
        with self.assertRaises(ValueError):
            parse_judge_output("no json here")


class TestJudgeRun(unittest.TestCase):
    def setUp(self):
        self.run_dir = Path(tempfile.mkdtemp())
        workspace = self.run_dir / "workspace"
        shutil.copytree(FIXTURES_DIR / "mock_solution_good", workspace)

        score = score_workspace(BENCHMARK_DIR, workspace)
        (self.run_dir / "score.json").write_text(json.dumps(score))
        manifest = {"run_id": "test-run", "benchmark": "basic-001-muon-scintillator"}
        (self.run_dir / "manifest.json").write_text(json.dumps(manifest))

    def tearDown(self):
        shutil.rmtree(self.run_dir, ignore_errors=True)

    def test_judge_updates_manual_review_criteria(self):
        before = json.loads((self.run_dir / "score.json").read_text())
        self.assertTrue(before["criteria"]["physics_plausibility"]["manual_review"])

        after = judge_run(
            run_dir=self.run_dir,
            benchmark_dir=BENCHMARK_DIR,
            command_template=FAKE_JUDGE_COMMAND,
            model="fake-model",
            timeout=30,
        )

        self.assertFalse(after["criteria"]["physics_plausibility"]["manual_review"])
        self.assertEqual(after["criteria"]["physics_plausibility"]["score"], 7)
        self.assertTrue(after["criteria"]["physics_plausibility"]["judged"])
        self.assertFalse(after["criteria"]["build_and_run"]["manual_review"])
        self.assertFalse(after["criteria"]["output"]["manual_review"])
        # criteria the static evaluator already scored confidently are untouched
        self.assertFalse(after["criteria"]["physics"]["manual_review"])
        self.assertFalse(after["needs_manual_review"])
        self.assertTrue((self.run_dir / "judge.log").exists())

    def test_malformed_judge_output_leaves_manual_review_set(self):
        after = judge_run(
            run_dir=self.run_dir,
            benchmark_dir=BENCHMARK_DIR,
            command_template=BROKEN_JUDGE_COMMAND,
            model="fake-model",
            timeout=30,
        )
        self.assertTrue(after["criteria"]["physics_plausibility"]["manual_review"])
        self.assertIn("judge failed", after["criteria"]["physics_plausibility"]["notes"])


if __name__ == "__main__":
    unittest.main()
