"""Decision regressions for the read-only Stage 2 replay."""

import copy
import json
import os
from pathlib import Path
import unittest

from stage2 import Profile, evaluate, load_profiles


BAKERS = "DISTRICT_CSC_BAKERS_QUARTER"
WIND = "BUILDING_CSC_BAKERS_WIND_MILL"
WATER = "BUILDING_CSC_BAKERS_WATER_MILL"
GRANARY = "BUILDING_GRANARY"
FARM = "IMPROVEMENT_FARM"
CENTER = "DISTRICT_CITY_CENTER"
PROFILES = {
    BAKERS: Profile(
        {WIND: frozenset(("TECH_MACHINERY",)), WATER: frozenset(("TECH_ENGINEERING",))},
        {CENTER: {GRANARY: frozenset(("TECH_POTTERY",))}},
        {"RESOURCE_WHEAT": frozenset((FARM,)), "RESOURCE_MAIZE": frozenset((FARM,))},
        frozenset(("RESOURCE_COCOA",)),
        "CIVIC_FEUDALISM",
    )
}


def fixture():
    return dict(unlocked=[], chains=[dict(
        district=BAKERS, city=1, plot=10, state="complete",
        materials=[
            dict(plot=11, resource="RESOURCE_WHEAT", viable=True, working=False,
                 work=dict(kind="improve", improvement=FARM, eligible=True, covered=False)),
            dict(plot=12, resource="RESOURCE_COCOA", viable=True, working=False),
        ],
        producers=[dict(building=WIND, state="available"),
                   dict(building=WATER, state="unavailable")],
        customers=[dict(city=2, plot=15, district=CENTER, state="complete",
                        buildings=[dict(building=GRANARY, state="available")])],
    )])


class Stage2Test(unittest.TestCase):
    def setUp(self):
        self.snapshot = fixture()
        self.chain = self.snapshot["chains"][0]

    def replay(self):
        return evaluate(PROFILES, self.snapshot)

    def test_first_mill_and_adjacent_granary(self):
        result = self.replay()
        self.assertEqual([(b["kind"], b["target"], b["city"]) for b in result["proposals"]],
                         [("build", WIND, 1), ("build", GRANARY, 2)])
        self.assertEqual(result["uncoveredWorkPlots"], [])
        self.assertEqual([(p["supply"], p["lastViable"], p["lastWorking"])
                          for p in result["protection"]],
                         [("base", True, False), ("specialty", True, False)])

    def test_work_uses_existing_cross_city_builder_capacity(self):
        self.chain["producers"][0]["state"] = "working"
        work = self.chain["materials"][0]["work"]
        work.update(kind="repair", covered=True)
        self.assertEqual([b["kind"] for b in self.replay()["proposals"]], ["build", "repair"])
        self.assertEqual(self.replay()["uncoveredWorkPlots"], [])
        work["covered"] = False
        other = copy.deepcopy(self.chain)
        other["plot"] = 18
        self.snapshot["chains"].append(other)
        result = self.replay()
        self.assertEqual(result["uncoveredWorkPlots"], [11])
        self.assertEqual([p["quarterPlot"] for p in result["protection"] if p["plot"] == 11], [10, 18])
        work["covered"] = None
        self.snapshot["chains"].pop()
        self.assertEqual(self.replay()["uncoveredWorkPlots"], [])

    def test_service_unlock_and_loss_of_last_working_supplier(self):
        self.chain["producers"][0]["state"] = "working"
        self.chain["customers"][0]["buildings"][0]["state"] = "working"
        self.chain["materials"][0]["working"] = True
        self.chain["materials"].append(dict(plot=14, resource="RESOURCE_MAIZE", viable=True))
        self.assertEqual([b["target"] for b in self.replay()["proposals"]], ["CIVIC_FEUDALISM"])
        self.snapshot["unlocked"] = ["CIVIC_FEUDALISM"]
        result = self.replay()
        self.assertEqual(result["proposals"], [])
        wheat = next(p for p in result["protection"] if p["plot"] == 11)
        self.assertFalse(wheat["lastViable"])
        self.assertTrue(wheat["lastWorking"])
        self.assertTrue(wheat["serviceAtRisk"])
        self.chain["state"] = "pillaged"
        self.assertFalse(any(p["serviceAtRisk"] for p in self.replay()["protection"]))

    def test_preference_bands_and_unlocks(self):
        self.chain["producers"][0].update(state="locked", unlock="TECH_MACHINERY")
        self.assertEqual([b["target"] for b in self.replay()["proposals"]], [GRANARY])
        self.chain["materials"].append(dict(plot=14, resource="RESOURCE_MAIZE", viable=True))
        bid = self.replay()["proposals"][0]
        self.assertEqual((bid["kind"], bid["target"], bid["band"]),
                         ("research", "TECH_MACHINERY", "preferred"))
        self.chain["producers"][0]["state"] = "working"
        work = self.chain["materials"][0]["work"]
        work.update(eligible=False, unlock="TECH_IRRIGATION")
        self.assertEqual([b["target"] for b in self.replay()["proposals"]], [GRANARY, "TECH_IRRIGATION"])
        work.update(eligible=True, improvement="IMPROVEMENT_MINE")
        self.assertEqual([b["target"] for b in self.replay()["proposals"]], [GRANARY])

    def test_candidate_uses_specific_future_customer_and_viable_base(self):
        self.chain.update(state="candidate", eligible=True, adjacency=4)
        self.chain["customers"][0].update(state="candidate", eligible=False)
        bid = self.replay()["proposals"][0]
        self.assertEqual((bid["kind"], bid["band"], bid["customerPath"]), ("place", "preferred", False))
        self.chain["customers"][0]["eligible"] = True
        self.assertTrue(self.replay()["proposals"][0]["customerPath"])
        self.chain["materials"][0]["viable"] = False
        self.assertEqual(self.replay()["proposals"], [])

    @unittest.skipUnless(os.environ.get("CSC_STAGE2_DB"), "set CSC_STAGE2_DB to a closed gameplay snapshot")
    def test_current_gameplay_profiles(self):
        profiles = load_profiles(Path(os.environ["CSC_STAGE2_DB"]))
        bakers = profiles[BAKERS]
        self.assertIn(FARM, bakers.base["RESOURCE_WHEAT"])
        self.assertIn(GRANARY, bakers.customers[CENTER])
        self.assertEqual(bakers.producers[WATER], frozenset(("TECH_ENGINEERING",)))
        self.assertEqual(bakers.service_unlock, "CIVIC_FEUDALISM")
        tailors = profiles["DISTRICT_CSC_TAILORS_QUARTER"]
        self.assertIn("BUILDING_LIGHTHOUSE", tailors.customers["DISTRICT_HARBOR"])
        self.assertEqual(tailors.service_unlock, "CIVIC_NAVAL_TRADITION")

        # Use existing captured facts only. Kerma has working suppliers and
        # Workshop, but its observed Amphitheater is a Stage 4 customer.
        source = Path(__file__).with_name("fixtures") / "captured_sites.json"
        sites = json.loads(source.read_text(encoding="utf-8"))["sites"]
        site = next(s for s in sites if s["id"] == "candidate150:p1:c393221:TAILORS:2165")
        result = evaluate(profiles, dict(chains=[dict(
            district="DISTRICT_CSC_TAILORS_QUARTER",
            city=site["identity"]["city"], plot=site["identity"]["plot"],
            state="complete",
            materials=[dict(m, viable=m["owned"] and m["revealed"] and m["district_free"])
                       for m in site["materials"]],
            producers=[dict(building="BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP", state="working")],
            customers=[dict(c, state="complete", buildings=[dict(building=c["building"], state="working")])
                       for c in site["customers"] if c["district_functioning"] and c["functioning"]],
        )]))
        self.assertEqual(result["proposals"], [])
        self.assertEqual([(p["plot"], p["supply"], p["lastViable"], p["lastWorking"])
                          for p in result["protection"]],
                         [(2166, "base", True, True), (2091, "specialty", True, True)])


if __name__ == "__main__":
    unittest.main()
