"""Compare the diagnostic shortlist with the normal planner in one archived game."""

from collections import Counter, defaultdict
import argparse
import json
from pathlib import Path
import re


MARKER = re.compile(r"\b(CSC_SHORTLIST_(?:SCOPE|PASS|WATCH|ERROR)|CSC_AI_(?:SPATIAL_BID|ECONOMY_PLAN|PLAN_EVENT|PROCESSING))\b(.*)")
FIELD = re.compile(r"(\w+)=([^\s]+)")


def fields(tail):
    return {k: int(v) if v.lstrip("-").isdigit() else v for k, v in FIELD.findall(tail)}


def counts(rows):
    calls = sum(r["calls"] for r in rows)
    kept = sum(r["kept"] for r in rows)
    winners = [r for r in rows if r["winner"] >= 0]
    misses = [r for r in winners if r["winner"] != r["alternate"]]
    return dict(scopes=len(rows), cold=sum(r["cold"] for r in rows), calls=calls,
                kept=kept, skipped=calls-kept, winners=len(winners), exact=len(winners)-len(misses),
                equal_value=sum(r["bid"] == r["alternateBid"] for r in misses),
                lost_bid=sum(r["alternate"] < 0 for r in misses),
                within_five_percent=sum(0 < r["bid"]-r["alternateBid"] <= r["bid"]*.05 for r in misses))


def analyze(log, first, last):
    scopes, passes, normal, published = {}, {}, {}, {}
    customer_plots = {}
    selected = set()
    plans = Counter()
    watches = []
    failures = []
    for line in log:
        match = MARKER.search(line)
        if not match:
            continue
        tag, tail = match.groups()
        if tag == "CSC_SHORTLIST_ERROR":
            failures.append(tail.strip())
            continue
        if tag == "CSC_SHORTLIST_PASS":
            turn, pid, number = map(int, tail.split())
            if first <= turn <= last:
                assert (turn, pid) not in passes, (turn, pid)
                passes[turn, pid] = number
            continue
        row = fields(tail)
        if not first <= row["turn"] <= last:
            continue
        turn = row["turn"]
        if tag == "CSC_AI_PROCESSING":
            assert turn not in published, turn
            published[turn] = (row["ok"], row["published"])
        elif tag == "CSC_AI_ECONOMY_PLAN":
            plans[turn, row["player"]] += 1
        elif tag == "CSC_AI_PLAN_EVENT":
            if row["kind"] == "selected" and row["reason"] == "native_best":
                selected.add((row["forecastTurn"],row["player"],row["city"],row["district"],row["plot"]))
        elif tag == "CSC_SHORTLIST_WATCH":
            watches.append(row)
        else:
            key = turn, row["player"], row["city"], row["district"]
            if tag == "CSC_SHORTLIST_SCOPE":
                assert key not in scopes and 0 < row["kept"] <= row["calls"], key
                scopes[key] = row
            elif row["rank"] == 1:
                assert key not in normal, key
                normal[key] = row["plot"], row["finalQ8"]
                customer_plots[key] = {row.get("customerPlot1",-1), row.get("customerPlot2",-1)}

    # An absent observer can otherwise look like a short period of perfect recall.
    assert not failures, failures
    assert set(published) == set(range(first, last+1)), "Missing turn boundaries"
    assert set(published.values()) == {(1, 1)}, Counter(published.values())
    assert plans and passes.keys() == plans.keys() and set(plans.values()) == {1}, "Player pass mismatch"
    actual_scopes = Counter(key[:2] for key in scopes)
    assert all(actual_scopes[key] == n for key, n in passes.items()), "Scope count mismatch"
    leaders = {key: (r["winner"], r["bid"]) for key, r in scopes.items() if r["winner"] >= 0}
    assert leaders == normal, "Observer's full ranking differs from the normal publisher"

    groups = defaultdict(list)
    episodes = {}
    gaps = []
    miss_context = Counter()
    confirmed = Counter()
    after_empty = Counter()
    for key, row in sorted(scopes.items()):
        turn, pid, city, district = key
        groups["all"].append(row)
        groups[row["quarter"]].append(row)
        groups["turns %d–%d" % (turn-(turn-1)%50, turn+49-(turn-1)%50)].append(row)
        # Price out a possible change against the actual shadow history. The
        # history of a modified selector would diverge after the first change.
        prior = turn-1, pid, city, district
        if scopes.get(prior,{}).get("alternate",-1) < 0:
            after_empty["extra_calls"] += row["calls"]-row["kept"]
            after_empty["misses_covered"] += row["winner"] != row["alternate"]
        if row["winner"] < 0:
            continue
        if (*key,row["winner"]) in selected:
            confirmed["full leaders selected by native AI"] += 1
            if row["winner"] != row["alternate"]:
                confirmed["missed leaders selected by native AI"] += 1
        if row["quarter"] == "TAILORS" and row["harbor"]:
            groups["Tailors leader with a possible or built Harbor"].append(row)
        if row["base"] and row["spec"]:
            groups["leader with Base and Spec"].append(row)
        if row["quarter"] == "TAILORS" and row["harbor"] and row["base"]:
            groups["Tailors leader with Base and a possible or built Harbor"].append(row)
        if (turn-1, pid, city, district) not in leaders:
            groups["first bid after an empty or absent scope"].append(row)
        if row["winner"] != row["alternate"]:
            if prior not in normal:
                miss_context["preceding turn had no positive full bid"] += 1
            elif row["winner"] in customer_plots[prior]:
                miss_context["previous full leader listed this plot for a customer"] += 1
            else:
                miss_context["other change of leader"] += 1
            plot_key = pid, city, district, row["winner"]
            gap = (row["bid"]-row["alternateBid"])/256
            gaps.append(gap)
            item = episodes.setdefault(plot_key, dict(player=pid, city=city, quarter=row["quarter"],
                plot=row["winner"], first=turn, last=turn, missed_turns=0, worst_gap=0))
            item["last"] = turn
            item["missed_turns"] += 1
            item["worst_gap"] = max(item["worst_gap"], gap)
    return dict(turns=[first,last], passes=len(passes), checked_rankings=len(normal),
                groups={label: counts(rows) for label,rows in groups.items()},
                missed_sites=sorted(episodes.values(), key=lambda r: -r["worst_gap"]),
                miss_context=dict(miss_context),
                new_native_selections=dict(confirmed),
                full_refresh_after_no_shadow_bid=dict(after_empty),
                mean_gap_when_site_differs=sum(gaps)/len(gaps) if gaps else None,
                watches_closed=len(watches),
                watch_endings=dict(Counter(str(w["occupant"]) for w in watches)),
                turns_to_reprice=dict(Counter(w["turn"]-w["start"] for w in watches if w["repriced"])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path)
    args = parser.parse_args()
    start = json.loads((args.game/"shortlist.json").read_text())["first_turn"]
    end = json.loads((args.game/"protocol.json").read_text())["endpoint"]
    with (args.game/"Lua.log").open(encoding="utf-8-sig", errors="replace") as stream:
        report = analyze(stream, start, end)
    print(json.dumps(report, indent=2))
