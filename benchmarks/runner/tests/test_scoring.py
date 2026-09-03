import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.scoring import score_workspace  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "basic-001-muon-scintillator"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestScoring(unittest.TestCase):
    def test_good_fixture_scores_well(self):
        result = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_good")
        # Without a Geant4 install, build_and_run and physics_plausibility are
        # always manual_review here -- check the criteria that static
        # analysis can actually decide.
        self.assertGreater(result["criteria"]["geometry"]["score"], 10)
        self.assertGreater(result["criteria"]["primary_source"]["score"], 10)
        self.assertEqual(result["criteria"]["physics"]["score"], 10)
        self.assertGreater(result["criteria"]["energy_scoring"]["score"], 15)
        self.assertGreater(result["criteria"]["idiomatic_geant4"]["score"], 3)

    def test_bad_fixture_scores_poorly(self):
        result = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_bad")
        self.assertEqual(result["criteria"]["physics"]["score"], 0)
        self.assertEqual(result["criteria"]["energy_scoring"]["score"], 0)
        self.assertLess(result["criteria"]["idiomatic_geant4"]["score"], 2)

    def test_good_beats_bad_on_automated_score(self):
        good = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_good")
        bad = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_bad")
        self.assertGreater(good["automated_score"], bad["automated_score"])

    def test_all_rubric_criteria_are_reported(self):
        result = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_good")
        import yaml

        rubric = yaml.safe_load((BENCHMARK_DIR / "rubric.yaml").read_text())
        expected_ids = {c["id"] for c in rubric["criteria"]}
        self.assertEqual(set(result["criteria"].keys()), expected_ids)

    def test_physics_plausibility_always_flagged_manual_review(self):
        result = score_workspace(BENCHMARK_DIR, FIXTURES_DIR / "mock_solution_good")
        self.assertTrue(result["criteria"]["physics_plausibility"]["manual_review"])
        self.assertTrue(result["needs_manual_review"])


if __name__ == "__main__":
    unittest.main()
