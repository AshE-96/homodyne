import unittest
from bluff_lab import value, cluster_ci, summaries, plan, demo


class ScientificChecks(unittest.TestCase):
    def test_ranking_reverses_without_changing_responses(self):
        d = demo()['scores_per_100']
        self.assertGreater(d['0']['A'], d['0']['B'])
        self.assertLess(d['3']['A'], d['3']['B'])

    def test_translation_clusters_not_counted_as_independent(self):
        r = cluster_ci([('q1', 1), ('q1', 1), ('q2', -1), ('q2', -1)], 500)
        self.assertEqual(r['n_clusters'], 2)
        self.assertEqual(r['n_prompts'], 4)
        self.assertEqual(r['ci95_pointwise'], [-1., 1.])

    def test_zero_coverage_has_undefined_conditional_risk(self):
        r = {'model':'silent', 'item_id':'u1', 'cluster_id':'u1', 'repeat':'1',
             'answerable':'false', 'label':'abstain'}
        s = summaries([r], 3, .05)['silent']
        self.assertIsNone(s['risk_among_answered'])
        self.assertEqual(s['score_points_per_prompt'], 0)
        self.assertEqual(s['guardrail']['status'], 'UNKNOWN')

    def test_errors_not_silently_deleted(self):
        self.assertEqual(value('api_error', 3), -3)
        self.assertEqual(value('invalid', 3), -3)

    def test_power_scales_with_difference_variance(self):
        self.assertAlmostEqual(plan(2, 400, .1)['mde_points_per_prompt'],
                               2*plan(1, 400, .1)['mde_points_per_prompt'])


if __name__ == '__main__':
    unittest.main()
