import unittest
from rent_pipeline import build
class TestRentPipeline(unittest.TestCase):
 def test_exact_match_and_provenance(self):
  ours={"locations":[{"id":"x","city":"Asunción","country":"Paraguay"}]}
  src={"cities":[{"name":"Asuncion","country":"Paraguay","metrics":{"cost":{"rent1brUsd":{"value":450,"asOf":"2026-11-17","sourceId":"city-source","level":"city"}}}}]}
  result=build(ours,src)
  self.assertEqual(result["stats"]["matched"],1)
  self.assertEqual(result["records"][0]["rent"]["rent1brUsd"]["usd"],450)
  self.assertFalse(result["publicationAllowed"])
 def test_ambiguous_not_silently_chosen(self):
  ours=[{"id":"x","city":"Paris","country":"France"}]
  c={"name":"Paris","country":"France","metrics":{"cost":{"rent1brUsd":{"value":900}}}}
  self.assertEqual(build(ours,[c,c])["stats"]["ambiguous"],1)
 def test_missing_is_null(self):
  r=build([{"id":"x","city":"No City","country":"No Country"}],[])
  self.assertIsNone(r["records"][0]["rent"])
 def test_zero_not_a_rent(self):
  r=build([{"id":"x","city":"Paris","country":"France"}],[{"name":"Paris","country":"France","metrics":{"cost":{"rent1brUsd":{"value":0}}}}])
  self.assertEqual(r["stats"]["no_rent"],1)
if __name__=="__main__":unittest.main()
