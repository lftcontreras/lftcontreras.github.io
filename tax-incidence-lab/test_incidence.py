"""Artificial mathematical fixtures only; never dissertation estimates."""
import unittest
from incidence import summarize


class IncidenceTests(unittest.TestCase):
    def fixture(self):
        return [dict(income=y, tax_before=y * .2, cashback=0., weight=1.) for y in (1., 2., 3., 4.)]

    def test_known_gini_and_proportional_tax(self):
        result = summarize(self.fixture())
        self.assertAlmostEqual(result['gini'], .25)
        self.assertAlmostEqual(result['kakwani_before'], 0.)
        self.assertAlmostEqual(sum(b['weight'] for b in result['deciles']), 4.)
        self.assertTrue(all(abs(b['burden_before_pct'] - 20) < 1e-10 for b in result['deciles']))

    def test_regressive_flat_tax(self):
        rows = self.fixture()
        for r in rows:
            r['tax_before'] = .1
        self.assertAlmostEqual(summarize(rows)['kakwani_before'], -.25)

    def test_targeted_cashback(self):
        rows = self.fixture()
        rows[0]['cashback'] = .1
        result = summarize(rows)
        self.assertAlmostEqual(result['deciles'][0]['burden_after_pct'], 10.)
        self.assertGreater(result['kakwani_after'], result['kakwani_before'])

    def test_ties_order_and_weight_scale(self):
        rows = self.fixture() + [dict(income=1., tax_before=.1, cashback=.05, weight=2.)]
        a, b = summarize(rows), summarize(list(reversed(rows)))
        self.assertEqual(a, b)
        scaled = summarize([dict(r, weight=r['weight'] * 5) for r in rows])
        self.assertAlmostEqual(a['kakwani_after'], scaled['kakwani_after'])
        for x, y in zip(a['deciles'], scaled['deciles']):
            self.assertAlmostEqual(x['burden_after_pct'], y['burden_after_pct'])

    def test_zero_tax_is_undefined(self):
        rows = self.fixture()
        for r in rows:
            r['cashback'] = r['tax_before']
        self.assertIsNone(summarize(rows)['kakwani_after'])

    def test_invalid_inputs(self):
        for field, value in [('income', 0.), ('income', float('nan')), ('weight', -1.), ('cashback', 999.)]:
            rows = self.fixture()
            rows[0][field] = value
            with self.assertRaises(ValueError):
                summarize(rows)
        with self.assertRaises(ValueError):
            summarize([])


if __name__ == '__main__':
    unittest.main()
