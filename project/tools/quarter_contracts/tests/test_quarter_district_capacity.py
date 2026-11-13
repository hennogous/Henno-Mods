"""Active Quarters must pay the district-slot opportunity cost in the design.

Execute the actual district INSERTs in SQLite. This checks the shipped values,
not just a comment, so the previous RequiresPopulation=0 regression is caught.
Native placement and save compatibility still require a fresh-game check.
"""
from pathlib import Path
import re
import sqlite3
import unittest


ROOT = Path(__file__).resolve().parents[4]


class QuarterDistrictCapacity(unittest.TestCase):
    def test_both_active_quarters_consume_a_slot_and_remain_one_per_city(self):
        for key in ("BAKERS", "TAILORS"):
            with self.subTest(quarter=key):
                source = (ROOT / f"Civ Supply Chains/Data/CSC_Q_{key}.sql").read_text(
                    encoding="utf-8-sig")
                statement = re.search(
                    r"^INSERT OR IGNORE INTO Districts\b.*?^\s*\);", source,
                    re.MULTILINE | re.DOTALL).group()
                columns = re.search(r"Districts\s*\((.*?)\)\s*VALUES", statement,
                                    re.DOTALL).group(1).split(",")
                with sqlite3.connect(":memory:") as db:
                    db.execute("CREATE TABLE Districts (" + ",".join(
                        '"' + column.strip() + '"' for column in columns) + ")")
                    db.executescript(statement)
                    rows = db.execute(
                        "SELECT DistrictType, RequiresPopulation, OnePerCity FROM Districts"
                    ).fetchall()
                self.assertEqual(rows, [(f"DISTRICT_CSC_{key}_QUARTER", 1, 1)])


if __name__ == "__main__":
    unittest.main()
