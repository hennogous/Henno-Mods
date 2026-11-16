"""Stage 3 population transaction registry and shared-scanner contract."""

from __future__ import annotations

import re
import math

try:
    from lupa import LuaRuntime
except ImportError:
    LuaRuntime = None
import sqlite3
import sys
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
        sys.path.insert(0, str(ROOT / "project/tools/transactions"))
        from population_catalogue_fixture import compile_catalogue
        self.connection = compile_catalogue(lgd=False)
        self.connection.row_factory = None

    def tearDown(self) -> None:
        self.connection.close()

    @unittest.skipIf(LuaRuntime is None, "lupa is required to execute gameplay Lua")
    def test_binary_rates_preserve_reported_transaction_totals(self) -> None:
        source = LUA.read_text(encoding="utf-8")
        helper = source.split("local function CSC_GetScaledPerPopulationAmount", 1)[1]
        helper = helper.split("local function CSC_WriteAmountBits", 1)[0]
        runtime = LuaRuntime()
        runtime.execute(
            "local AMOUNT_SCALE = 256; local MAX_STAGE3_SCALED_RATE = 32767; "
            "function encode" + helper
        )
        for target, population, displayed in (
            (1.01, 10, 1.0), (2.02, 10, 2.0), (1.01, 5, 1.0),
            (0.101, 26, 0.1), (0, 10, 0), (1.01, 0, 0),
        ):
            with self.subTest(target=target, population=population):
                encoded = runtime.globals().encode(target, population)
                bits = [1 << index for index in range(15) if encoded & (1 << index)]
                # Each SQL coefficient survives individual Q8 truncation exactly.
                native_rate = sum(math.floor(bit / 256 * 256) / 256 for bit in bits)
                total = native_rate * population
                self.assertEqual(math.floor(total * 10) / 10, displayed)
                if target > 0 and population > 0:
                    self.assertGreaterEqual(total, target)
                    self.assertLess(total - target, population / 256)

    def test_stage3_uses_fifteen_bits_and_retains_stage4_range(self) -> None:
        shared = (DATA / "CSC_Q_ALL.sql").read_text(encoding="utf-8-sig")
        for table in ("CSC_ScaledAmountBits", "CSC_Stage3RateBits", "CSC_Stage4StackBits"):
            self.connection.executescript(
                _statement(shared, "CREATE TABLE IF NOT EXISTS " + table)
            )
            for statement in re.findall(
                rf"^INSERT OR IGNORE INTO {table}\b[^;]*;", shared, re.MULTILINE | re.DOTALL
            ):
                self.connection.executescript(statement)
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*), MAX(Bit) FROM CSC_Stage3RateBits").fetchone(),
            (15, 16384),
        )
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*), MAX(Bit) FROM CSC_Stage4StackBits").fetchone(),
            (20, 524288),
        )
        for quarter in ("BAKERS", "TAILORS"):
            for suffix in ("", "_GOLD"):
                sql = (DATA / f"CSC_Q_{quarter}{suffix}.sql").read_text(encoding="utf-8-sig")
                self.assertNotIn("Bit / 10000.0", sql)
                self.assertNotIn("FROM CSC_ScaledAmountBits", sql)
        processor = (DATA / "CSC_BuildingTransactionProcessor.sql").read_text(encoding="utf-8")
        self.assertIn("/ 256.0", processor)

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
                    "CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT_Q8", "CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8", 0.101,
                ),
                (
                    "CSC_TAILORS_TAILOR_MARKET", "BUILDING_CSC_TAILORS_TAILOR", "DISTRICT_COMMERCIAL_HUB",
                    "BUILDING_MARKET", "CSC_TAILORS_STAGE_3_CUSTOMER_POP",
                    "CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8", "CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT_Q8", 0.101,
                ),
                (
                    "CSC_TAILORS_TAILOR_TEMPLE", "BUILDING_CSC_TAILORS_TAILOR", "DISTRICT_HOLY_SITE",
                    "BUILDING_TEMPLE", "CSC_TAILORS_STAGE_3_CUSTOMER_POP",
                    "CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8", "CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT_Q8", 0.101,
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
