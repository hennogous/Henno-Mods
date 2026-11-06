"""Replay the first CSC Stage 2 decision slice on copied, player-local facts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3


# The planning tables describe producers and customers, but omit Service unlocks.
# Only enable that bid for reviewed gameplay requirement sets.
SERVICE_GATES = {
    "BAKERS": "REQSET_CSC_STAGE_2_EFFECT_PREREQ",
    "TAILORS": "REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ",
}


@dataclass(frozen=True)
class Profile:
    producers: dict[str, frozenset[str]]
    customers: dict[str, dict[str, frozenset[str]]]
    base: dict[str, frozenset[str]]
    specialty: frozenset[str]
    service_unlock: str | None


def load_profiles(db_path: Path) -> dict[str, Profile]:
    """Read a closed DebugGameplay snapshot. No game or CE is needed."""
    uri = db_path.resolve().as_uri() + "?mode=ro&immutable=1"
    with sqlite3.connect(uri, uri=True) as db:
        profiles = {}
        host_replacements = {}
        for variant, standard in db.execute(
            "SELECT CivUniqueDistrictType, ReplacesDistrictType FROM DistrictReplaces"
        ):
            host_replacements.setdefault(standard, []).append(variant)
        districts = db.execute("""
            SELECT DISTINCT f.QuarterKey, b.PrereqDistrict
            FROM CSC_QuarterFlowBuildings f JOIN Buildings b USING (BuildingType)
            WHERE f.Stage = 2 ORDER BY f.QuarterKey
        """).fetchall()
        for key, district in districts:
            producers = {}
            for name, tech, civic in db.execute("""
                SELECT b.BuildingType, b.PrereqTech, b.PrereqCivic
                FROM CSC_QuarterFlowBuildings f JOIN Buildings b USING (BuildingType)
                WHERE f.Stage = 2 AND f.QuarterKey = ? AND b.PrereqDistrict = ?
            """, (key, district)):
                producers[name] = frozenset(filter(None, (tech, civic)))

            # Use the actual host district of each loaded building, including
            # direct unique replacements such as a unique Harbor/Lighthouse pair.
            customers = {}
            for name, host, tech, civic in db.execute("""
                SELECT b.BuildingType, b.PrereqDistrict, b.PrereqTech, b.PrereqCivic
                FROM CSC_QuarterCustomerBuildings c JOIN Buildings b
                  ON b.BuildingType = c.BuildingType OR b.BuildingType IN (
                    SELECT CivUniqueBuildingType FROM BuildingReplaces
                    WHERE ReplacesBuildingType = c.BuildingType
                  )
                WHERE c.ProducerStage = 2 AND c.QuarterKey = ? AND (
                    b.PrereqDistrict = c.DistrictType OR b.PrereqDistrict IN (
                        SELECT CivUniqueDistrictType FROM DistrictReplaces
                        WHERE ReplacesDistrictType = c.DistrictType
                    )
                )
            """, (key,)):
                unlocks = frozenset(filter(None, (tech, civic)))
                for site_type in (host, *host_replacements.get(host, ())):
                    customers.setdefault(site_type, {})[name] = unlocks

            base = {}
            for resource, improvement in db.execute("""
                SELECT t.Type, v.ImprovementType
                FROM TypeTags t JOIN Resources r ON r.ResourceType = t.Type
                LEFT JOIN Improvement_ValidResources v ON v.ResourceType = t.Type
                WHERE t.Tag = ?
            """, (f"CLASS_CSC_{key}_BASE",)):
                options = base.setdefault(resource, set())
                if improvement is not None:
                    options.add(improvement)
            specialty = frozenset(resource for (resource,) in db.execute("""
                SELECT t.Type FROM TypeTags t JOIN Resources r ON r.ResourceType = t.Type
                WHERE t.Tag = ?
            """, (f"CLASS_CSC_{key}_SPEC",)))

            unlocks = db.execute("""
                SELECT DISTINCT a.Value
                FROM RequirementSetRequirements s JOIN RequirementArguments a USING (RequirementId)
                WHERE s.RequirementSetId = ? AND a.Name IN ('TechnologyType', 'CivicType')
            """, (SERVICE_GATES.get(key),)).fetchall()
            service_unlock = unlocks[0][0] if len(unlocks) == 1 else None
            profiles[district] = Profile(
                producers, customers, {r: frozenset(v) for r, v in base.items()},
                specialty, service_unlock,
            )
    return profiles


def _building_bids(options, definitions, city, plot, role, band, allow_unlock):
    for option in options:
        name = option["building"]
        if name not in definitions:
            continue
        state = option["state"]
        if state in ("available", "repairable"):
            yield dict(kind="repairBuilding" if state == "repairable" else "build",
                       target=name, city=city, plot=plot, role=role, band=band)
        elif allow_unlock and state == "locked" and option.get("unlock") in definitions[name]:
            yield dict(kind="research", target=option["unlock"], role=role, band=band)


def evaluate(profiles: dict[str, Profile], snapshot: dict) -> dict:
    """Return explainable proposals, in review bands rather than native units.

    The caller supplies revealed, adjacent observations scoped to one player.
    Viability and available actions come from the snapshot, including actual
    ownership, unlocks, terrain, reservations and each Mill's native eligibility.
    A work coverage fact accounts for assignment or a reachable worker with a
    free charge across cities. Unknown coverage never creates Builder demand.
    """
    known = set(snapshot["unlocked"]) if "unlocked" in snapshot else None
    proposals, protection, uncovered = [], [], set()
    for chain in snapshot["chains"]:
        profile = profiles.get(chain["district"])
        if profile is None:
            continue
        plot, city, state = chain["plot"], chain["city"], chain["state"]
        materials = {m["plot"]: m for m in chain["materials"] if m.get("viable") is True}
        base = [m for m in materials.values() if m["resource"] in profile.base]
        spec = [m for m in materials.values() if m["resource"] in profile.specialty]
        working_base = sum(m.get("working") is True for m in base)
        customers = [c for c in chain["customers"] if c["district"] in profile.customers]
        customer_ready = any(
            c["state"] == "complete" and any(
                o["state"] == "working" and o["building"] in profile.customers[c["district"]]
                for o in c["buildings"]
            ) for c in customers
        )
        producer_ready = any(
            b["state"] == "working" and b["building"] in profile.producers
            for b in chain["producers"]
        )
        service_ready = state == "complete" and producer_ready and customer_ready and working_base > 0

        # Report affected suppliers even for a temporarily pillaged Quarter.
        # A working supplier and a viable deposit answer different questions.
        if state in ("complete", "pillaged", "underConstruction"):
            for supply_class, supply in (("base", base), ("specialty", spec)):
                working = sum(m.get("working") is True for m in supply)
                for material in supply:
                    last_working = working == 1 and material.get("working") is True
                    protection.append(dict(
                        plot=material["plot"], quarterPlot=plot, supply=supply_class,
                        lastViable=len(supply) == 1, lastWorking=last_working,
                        serviceAtRisk=(supply_class == "base" and last_working and service_ready
                                       and known is not None and profile.service_unlock in known),
                    ))

        bids = []
        if state == "candidate" and chain.get("eligible") is True and base:
            customer_path = any(
                c["state"] == "complete" or (c["state"] == "candidate" and c.get("eligible") is True)
                for c in customers
            )
            bids.append(dict(kind="place", target=chain["district"], city=city, plot=plot,
                             band="preferred" if chain["adjacency"] >= 4 else "normal",
                             base=len(base), specialty=len(spec), customerPath=customer_path))
        if state == "complete" and base:
            if not producer_ready:
                bids.extend(_building_bids(
                    chain["producers"], profile.producers, city, plot, "producer",
                    "preferred" if len(base) >= 2 else "normal", allow_unlock=len(base) >= 2,
                ))
            for customer in customers:
                if customer["state"] == "complete":
                    bids.extend(_building_bids(
                        customer["buildings"], profile.customers[customer["district"]],
                        customer["city"], customer["plot"], "customer", "normal", allow_unlock=False,
                    ))
            if producer_ready:
                for material in base:
                    work = material.get("work")
                    if (material.get("working") is True or not work
                            or work["improvement"] not in profile.base[material["resource"]]
                            or work["kind"] not in ("improve", "repair")):
                        continue
                    if work.get("eligible") is True:
                        bids.append(dict(kind=work["kind"], target=work["improvement"],
                                         plot=material["plot"], band="preferred"))
                        if work.get("covered") is False:
                            uncovered.add(material["plot"])
                    elif work.get("unlock") and (known is None or work["unlock"] not in known):
                        bids.append(dict(kind="research", target=work["unlock"],
                                         role="improvement", band="normal"))
            if (service_ready and known is not None and profile.service_unlock
                    and profile.service_unlock not in known):
                bids.append(dict(kind="research", target=profile.service_unlock,
                                 role="service", band="preferred"))
        proposals.extend(dict(bid, quarterPlot=plot) for bid in bids)

    # Keep contributing Quarters visible. The adapter will coalesce equivalent
    # actions. Builder demand already counts a shared job only once.
    return dict(proposals=proposals, protection=protection, uncoveredWorkPlots=sorted(uncovered))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8-sig"))
    print(json.dumps(evaluate(load_profiles(args.database), snapshot), indent=2))
