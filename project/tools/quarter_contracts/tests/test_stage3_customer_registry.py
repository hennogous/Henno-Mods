"""Stage 3 population transaction registry and shared-scanner contract."""

from __future__ import annotations

import re
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "Civ Supply Chains/Data"
LUA = ROOT / "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"


def _statement(source: str, start: str) -> str:
    match = re.search(rf"^{re.escape(start)}\b[^;]*;", source, re.MULTILINE | re.DOTALL)
    assert match is not None, start
    return match.group()


class Stage3CustomerRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        shared = (DATA / "CSC_Q_ALL.sql").read_text(encoding="utf-8-sig")
        self.connection.executescript(
            _statement(shared, "CREATE TABLE IF NOT EXISTS CSC_Stage3CustomerTransactions")
        )
        for filename in ("CSC_Q_BAKERS.sql", "CSC_Q_TAILORS.sql"):
            source = (DATA / filename).read_text(encoding="utf-8-sig")
            self.connection.executescript(
                _statement(source, "INSERT OR IGNORE INTO CSC_Stage3CustomerTransactions")
            )

    def tearDown(self) -> None:
        self.connection.close()

    def test_each_customer_family_has_one_complete_row(self) -> None:
        rows = self.connection.execute(
            "SELECT TransactionId, SellerBuildingType, CustomerDistrictType, CustomerBuildingType, "
            "SellerPopulationProperty, SellerReturnAmountProperty, CustomerYieldAmountProperty, "
            "EngineAmountPerPopulation FROM CSC_Stage3CustomerTransactions ORDER BY TransactionId"
        ).fetchall()
        self.assertEqual(
            rows,
            [
                (
                    "CSC_BAKERS_BAKERY_MARKET", "BUILDING_CSC_BAKERS_BAKERY", "DISTRICT_COMMERCIAL_HUB",
                    "BUILDING_MARKET", "CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP",
                    "CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT", "CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT", 0.105,
                ),
                (
                    "CSC_TAILORS_TAILOR_MARKET", "BUILDING_CSC_TAILORS_TAILOR", "DISTRICT_COMMERCIAL_HUB",
                    "BUILDING_MARKET", "CSC_TAILORS_STAGE_3_CUSTOMER_POP",
                    "CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT", None, 0.105,
                ),
                (
                    "CSC_TAILORS_TAILOR_TEMPLE", "BUILDING_CSC_TAILORS_TAILOR", "DISTRICT_HOLY_SITE",
                    "BUILDING_TEMPLE", "CSC_TAILORS_STAGE_3_CUSTOMER_POP",
                    "CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT", None, 0.105,
                ),
            ],
        )

    def test_shared_scanner_preserves_customer_site_identity(self) -> None:
        source = LUA.read_text(encoding="utf-8")
        self.assertIn("for row in GameInfo.CSC_Stage3CustomerTransactions() do", source)
        self.assertIn('local transactionKey = transaction.Id .. ":" .. customerPlotKey;', source)
        self.assertIn("CSC_CreateDistrictReplacementFamily(row.CustomerDistrictType)", source)
        self.assertIn("CSC_CreateBuildingReplacementFamily(row.CustomerBuildingType)", source)
        self.assertIn("CSC_ScanStage3CustomerTransactions(cityStates, stage3SellerRecords, stage3CustomerCitiesByTransaction);", source)
        self.assertNotIn("CSC_ScanBakeryMarketTransactions", source)
        self.assertNotIn("CSC_ScanTailorCustomerTransactions", source)

    def test_registry_properties_feed_both_seller_yields_and_bakery_food(self) -> None:
        for quarter in ("BAKERS", "TAILORS"):
            core = (DATA / f"CSC_Q_{quarter}.sql").read_text(encoding="utf-8-sig")
            gold = (DATA / f"CSC_Q_{quarter}_GOLD.sql").read_text(encoding="utf-8-sig")
            rows = self.connection.execute(
                "SELECT DISTINCT SellerReturnAmountProperty, CustomerYieldAmountProperty "
                "FROM CSC_Stage3CustomerTransactions WHERE TransactionId LIKE ?",
                (f"CSC_{quarter}_%",),
            )
            for return_property, customer_property in rows:
                self.assertIn(return_property + "_BIT_", core)
                if customer_property is not None:
                    self.assertIn(customer_property + "_BIT_", core)
            gold_family = {
                "BAKERS": "MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_",
                "TAILORS": "MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_",
            }[quarter]
            self.assertIn(gold_family, gold)

    def test_registry_rejects_duplicate_customer_pair(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO CSC_Stage3CustomerTransactions "
                "(TransactionId, SellerDistrictType, SellerBuildingType, CustomerDistrictType, "
                "CustomerBuildingType, SellerPopulationProperty, SellerReturnAmountProperty, "
                "EngineAmountPerPopulation) "
                "SELECT 'CSC_DUPLICATE', SellerDistrictType, SellerBuildingType, CustomerDistrictType, "
                "CustomerBuildingType, SellerPopulationProperty, SellerReturnAmountProperty, "
                "EngineAmountPerPopulation FROM CSC_Stage3CustomerTransactions "
                "WHERE TransactionId='CSC_TAILORS_TAILOR_MARKET'"
            )


if __name__ == "__main__":
    unittest.main()
