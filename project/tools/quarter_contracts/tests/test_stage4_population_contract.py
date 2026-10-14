"""Guard the canonical Cafe method and exercise its actual gameplay Lua."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

try:
    from lupa import LuaRuntime
except ImportError:
    LuaRuntime = None

SCRIPT = Path(__file__).resolve().parents[1] / "validate_quarter.py"
SPEC = importlib.util.spec_from_file_location("stage4_contract_validator", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
LUA = VALIDATOR.ROOT / "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"
FIXTURE = Path(__file__).with_name("fixtures") / "cafe_stage4_world.lua"


class Stage4ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.implementation = VALIDATOR.load_yaml(VALIDATOR.SPEC_ROOT / "tailors/implementation.yaml")
        self.design = VALIDATOR.load_yaml(VALIDATOR.SPEC_ROOT / "tailors/design.yaml")
        self.requirement = next(
            requirement for requirement in VALIDATOR.flatten_requirements(self.implementation)
            if requirement["id"] == "I.STAGE4_POP_CUSTOMERS"
        )

    def errors(self, requirement=None, implementation=None) -> list[str]:
        result = VALIDATOR.Validation()
        VALIDATOR.validate_stage4_population_requirement(
            requirement or self.requirement, self.design,
            implementation or self.implementation, result,
        )
        return result.errors

    def test_current_stage4_binding_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_rejects_alternative_method_population_source_and_sum_rounding(self) -> None:
        for key, value in (
            ("canonical_reference", "original_cafe_sql"),
            ("method", "sql_population_thresholds"),
            ("population_source", "seller_city"),
            ("rounding", "floor_after_population_sum"),
            ("sql_effect", "MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION"),
            ("property_scope", "city_only"),
            ("deduplication_key", ["seller_city", "customer_city"]),
        ):
            with self.subTest(key=key):
                broken = copy.deepcopy(self.requirement)
                broken["implementation_binding"][key] = value
                self.assertTrue(any(key in error for error in self.errors(broken)))

    def test_interval_must_match_design(self) -> None:
        broken = copy.deepcopy(self.requirement)
        broken["implementation_binding"]["population_interval"] = 10
        self.assertTrue(any("referenced design" in error for error in self.errors(broken)))

    def test_cannot_bypass_method_by_removing_integer_pattern(self) -> None:
        broken = copy.deepcopy(self.requirement)
        broken["gameplay_patterns"].remove("GP.SCALING.PER_N_POPULATION_INTEGER")
        self.assertTrue(any("requires GP.SCALING.PER_N_POPULATION_INTEGER" in error for error in self.errors(broken)))

    def test_missing_or_unstructured_binding_fails(self) -> None:
        for binding in (None, "sql_only"):
            with self.subTest(binding=binding):
                broken = copy.deepcopy(self.requirement)
                broken["implementation_binding"] = binding
                self.assertTrue(self.errors(broken))

    def test_gameplay_output_must_be_declared_and_wired(self) -> None:
        output = self.requirement["implementation_binding"]["gameplay_output"]
        broken = copy.deepcopy(self.requirement)
        broken["outputs"].remove(output)
        self.assertTrue(any("outputs must include" in error for error in self.errors(broken)))
        broken_implementation = copy.deepcopy(self.implementation)
        broken_implementation["build_wiring"]["actions"][output]["type"] = "ImportFiles"
        self.assertTrue(any("gameplay action" in error for error in self.errors(implementation=broken_implementation)))
        broken_implementation["planned_outputs"][output] = "other.lua"
        self.assertTrue(any("shared customer-population Lua" in error for error in self.errors(implementation=broken_implementation)))

    def test_phase_must_require_population_output_and_lua_suite(self) -> None:
        broken = copy.deepcopy(self.implementation)
        phase = broken["phase_validation"]["stage4"]
        phase["required_outputs"].remove(self.requirement["implementation_binding"]["gameplay_output"])
        phase["required_suites"].remove("lua_contract")
        original_loader = VALIDATOR.load_yaml

        def load(path):
            if path == VALIDATOR.SPEC_ROOT / "tailors/implementation.yaml":
                return broken
            return original_loader(path)

        with mock.patch.object(VALIDATOR, "load_yaml", side_effect=load):
            result = VALIDATOR.validate_quarter("tailors", check_clean_start=True)
        self.assertTrue(any("stage4: phase validation omits requirement outputs" in error for error in result.errors))
        self.assertTrue(any("stage4: phase validation omits required suites lua_contract" in error for error in result.errors))


@unittest.skipIf(LuaRuntime is None, "Cafe gameplay behavior checks require the isolated lupa test dependency")
class CafeStage4BehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(FIXTURE.read_text(encoding="utf-8"))
        self.lua.execute(LUA.read_text(encoding="utf-8-sig"))
        self.lua.execute("""
            seller = addCity(1, 15);
            addDistrict(seller, 'DISTRICT_CSC_BAKERS_QUARTER', 0, 0);
            addBuilding(seller, 'BUILDING_CSC_BAKERS_CAFE');
            customer = addCity(2, 5);
            addDistrict(customer, 'DISTRICT_ENTERTAINMENT_COMPLEX', 1, 0);
            addBuilding(customer, 'BUILDING_ZOO');
        """)

    def refresh(self) -> None:
        self.lua.globals().CSC_RefreshCustomerPopulationReturns()

    def stacks(self, city: str, branch: str = "CAFE") -> int:
        suffix = "CAFE_RETURN" if branch == "CAFE" else branch + "_CULTURE_RETURN"
        property_name = "CSC_BAKERS_STAGE_4_" + suffix
        actual = self.lua.eval(f"{city}:GetProperty('{property_name}') or 0")
        # Check the delivery bridge too: both scopes encode exactly the raw stack.
        for scope in (city, city + ".center"):
            self.assertEqual(self.lua.eval(f"{scope}:GetProperty('{property_name}') or 0"), actual)
            encoded = sum(
                bit * self.lua.eval(f"{scope}:GetProperty('{property_name}_BIT_{bit}') or 0")
                for bit in (1 << index for index in range(20))
            )
            self.assertEqual(encoded, actual)
        return actual

    def test_customer_population_controls_both_sides(self) -> None:
        for seller_population, customer_population, expected in (
            (15, 5, 1), (5, 15, 3), (40, 15, 3),
        ):
            with self.subTest(seller=seller_population, customer=customer_population):
                self.lua.execute(f"seller.population={seller_population}; customer.population={customer_population}")
                self.refresh()
                self.assertEqual(self.stacks("seller"), expected)
                self.assertEqual(self.stacks("customer", "ZOO"), expected)

    def test_thresholds_and_population_above_sql_ladder(self) -> None:
        for population, expected in ((4, 0), (5, 1), (9, 1), (10, 2), (55, 11)):
            with self.subTest(population=population):
                self.lua.execute(f"customer.population={population}")
                self.refresh()
                self.assertEqual(self.stacks("seller"), expected)
                self.assertEqual(self.stacks("customer", "ZOO"), expected)

    def test_rounds_each_customer_before_sum(self) -> None:
        self.lua.execute("""
            customer.population=9;
            second=addCity(3, 9);
            addDistrict(second, 'DISTRICT_WATER_ENTERTAINMENT_COMPLEX', 0, 1);
            addBuilding(second, 'BUILDING_FERRIS_WHEEL');
        """)
        self.refresh()
        self.assertEqual(self.stacks("seller"), 2)
        self.assertEqual(self.stacks("customer", "ZOO"), 1)
        self.assertEqual(self.stacks("second", "FERRIS"), 1)

    def test_two_sites_in_one_city_stack_and_clear_independently(self) -> None:
        self.lua.execute("""
            addDistrict(customer, 'DISTRICT_WATER_ENTERTAINMENT_COMPLEX', 0, 1);
            addBuilding(customer, 'BUILDING_FERRIS_WHEEL');
        """)
        self.refresh()
        self.assertEqual(self.stacks("seller"), 2)
        self.assertEqual(self.stacks("customer", "ZOO"), 1)
        self.assertEqual(self.stacks("customer", "FERRIS"), 1)
        self.lua.execute("customer.pillagedBuildings[GameInfo.Buildings.BUILDING_ZOO.Index]=true")
        self.refresh()
        self.assertEqual(self.stacks("seller"), 1)
        self.assertEqual(self.stacks("customer", "ZOO"), 0)
        self.assertEqual(self.stacks("customer", "FERRIS"), 1)

    def test_two_sellers_supply_one_site(self) -> None:
        self.lua.execute("""
            otherSeller=addCity(3, 2);
            addDistrict(otherSeller, 'DISTRICT_CSC_BAKERS_QUARTER', 2, 0);
            addBuilding(otherSeller, 'BUILDING_CSC_BAKERS_CAFE');
        """)
        self.refresh()
        self.assertEqual(self.stacks("seller"), 1)
        self.assertEqual(self.stacks("otherSeller"), 1)
        self.assertEqual(self.stacks("customer", "ZOO"), 2)

    def test_same_city_transaction_and_direct_replacements(self) -> None:
        self.lua.execute("""
            customer.buildings={};
            addDistrict(seller, 'DISTRICT_STREET_CARNIVAL', 0, 1);
            addBuilding(seller, 'BUILDING_THERMAL_BATH');
        """)
        self.refresh()
        self.assertEqual(self.stacks("seller"), 3)
        self.assertEqual(self.stacks("seller", "ZOO"), 3)

    def test_ineligible_transaction_clears_previous_stack_and_bits(self) -> None:
        for change in (
            "seller.pillagedBuildings[GameInfo.Buildings.BUILDING_CSC_BAKERS_CAFE.Index]=true",
            "customer.buildings={}",
            "customer.owner=1",
            "customer.population=4",
        ):
            with self.subTest(change=change):
                self.setUp()
                self.refresh()
                self.assertEqual(self.stacks("seller"), 1)
                self.lua.execute(change)
                self.refresh()
                self.assertEqual(self.stacks("seller"), 0)
                self.assertEqual(self.stacks("customer", "ZOO"), 0)


if __name__ == "__main__":
    unittest.main()
