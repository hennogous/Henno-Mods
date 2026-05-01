"""
CSC Mod Test Harness via FireTuner

Example test suite for verifying CivSupplyChains mod functionality
in a running Civ 6 game. Run with a game loaded that has CSC active.

Usage:
    python firetuner_csc_test.py
"""

from firetuner_client import FireTuner
import sys
import time


class CSCTestHarness:
    """Test harness for CivSupplyChains mod via FireTuner."""
    
    def __init__(self, ft: FireTuner):
        self.ft = ft
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_all(self):
        """Run all test suites."""
        print("=" * 60)
        print("CSC Mod Test Suite")
        print("=" * 60)
        
        self.test_mod_loaded()
        self.test_types_registered()
        self.test_resources_exist()
        self.test_buildings_exist()
        self.test_modifiers_registered()
        
        print()
        print("=" * 60)
        total = self.passed + self.failed
        print(f"Results: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print("\nFailures:")
            for err in self.errors:
                print(f"  ✗ {err}")
        print("=" * 60)
        return self.failed == 0
    
    def check(self, name, lua_code, expected=None, check_fn=None):
        """
        Run a single test check.
        
        Args:
            name: Test description
            lua_code: Lua to execute (should return a value)
            expected: Expected string result (exact match)
            check_fn: Callable(result) -> bool for custom validation
        """
        result = self.ft.execute(lua_code, timeout=5.0)
        
        ok = False
        if expected is not None:
            ok = (result is not None and str(result).strip() == str(expected).strip())
        elif check_fn is not None:
            ok = check_fn(result)
        else:
            # Just check we got a non-None, non-empty response
            ok = result is not None and result.strip() != ''
        
        if ok:
            print(f"  ✓ {name}")
            self.passed += 1
        else:
            print(f"  ✗ {name} (got: {repr(result)})")
            self.failed += 1
            self.errors.append(f"{name}: expected {expected or 'truthy'}, got {repr(result)}")
    
    def check_exists(self, name, table, type_name):
        """Check if a type exists in GameInfo."""
        lua = f'local info = GameInfo.{table}["{type_name}"]; if info then return "exists" else return "nil" end'
        self.check(name, lua, expected="exists")
    
    # =====================================================
    # TEST SUITES
    # =====================================================
    
    def test_mod_loaded(self):
        """Verify the CSC mod is loaded."""
        print("\n--- Mod Loading ---")
        # Check if any CSC type exists (basic smoke test)
        self.check(
            "CSC mod types registered",
            'local count = 0; for row in GameInfo.Types() do if string.find(row.Type, "CSC_") then count = count + 1 end end; return tostring(count)',
            check_fn=lambda r: r is not None and int(r) > 0
        )
    
    def test_types_registered(self):
        """Verify core CSC types are in the database."""
        print("\n--- Core Types ---")
        types_to_check = [
            ("DISTRICT_CSC_BAKERS", "Districts"),
            ("IMPROVEMENT_CSC_BAKERS_WHEAT_FIELD", "Improvements"),
            ("RESOURCE_CSC_FLOUR", "Resources"),
        ]
        for type_name, table in types_to_check:
            self.check_exists(f"{type_name} in {table}", table, type_name)
    
    def test_resources_exist(self):
        """Verify CSC resources are registered."""
        print("\n--- Resources ---")
        resources = [
            "RESOURCE_CSC_FLOUR",
            "RESOURCE_CSC_BREAD",
        ]
        for res in resources:
            self.check_exists(f"{res}", "Resources", res)
    
    def test_buildings_exist(self):
        """Verify CSC buildings are registered."""
        print("\n--- Buildings ---")
        buildings = [
            "BUILDING_CSC_Q_BAKERS_FLOUR_MILL",
            "BUILDING_CSC_Q_BAKERS_BAKERY",
            "BUILDING_CSC_Q_BAKERS_CAFE",
        ]
        for bldg in buildings:
            self.check_exists(f"{bldg}", "Buildings", bldg)
    
    def test_modifiers_registered(self):
        """Verify CSC modifiers are in the database."""
        print("\n--- Modifiers ---")
        self.check(
            "CSC modifiers exist",
            'local count = 0; for row in GameInfo.Modifiers() do if string.find(row.ModifierId, "CSC_") then count = count + 1 end end; return tostring(count)',
            check_fn=lambda r: r is not None and int(r) > 0
        )


def main():
    ft = FireTuner()
    
    try:
        print("Connecting to Civ 6...")
        ft.connect()
        print("Connected!\n")
    except ConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nMake sure Civ 6 is running with a game loaded and EnableTuner=1 in AppOptions.txt")
        sys.exit(1)
    
    try:
        harness = CSCTestHarness(ft)
        success = harness.run_all()
        sys.exit(0 if success else 1)
    finally:
        ft.close()


if __name__ == '__main__':
    main()
