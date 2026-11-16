"""Audit derived AI district edges against loaded gameplay routing metadata.

Read-only diagnostic: the ordinary and population-scaled transaction registries
and gameplay sales/provider tags own relationships. This computes an expected
set, expands loaded replacements once, and compares the native SQL generator's output. It maintains no separate
Quarter/customer list. City Center and exact-Wonder hosts are explicitly routed
outside ordinary district-placement incentives.
"""
from collections import defaultdict
from contextlib import closing
from pathlib import Path
import argparse
import json
import sqlite3


def audit(db):
    districts = {r[0] for r in db.execute('SELECT DistrictType FROM Districts')}
    expected, excluded = defaultdict(set), []
    quarters = {q: q[len('DISTRICT_CSC_'):-len('_QUARTER')] for q in districts
                if q.startswith('DISTRICT_CSC_') and q.endswith('_QUARTER')}

    def add(customer, quarter, source):
        if customer in ('DISTRICT_CITY_CENTER', 'DISTRICT_WONDER'):
            excluded.append(dict(customer=customer, quarter=quarter, source=source))
        elif customer in districts and quarter in districts:
            expected[(customer, quarter)].add(source)

    for key, stage, customer in db.execute('SELECT QuarterKey,ProducerStage,DistrictType FROM CSC_QuarterCustomerBuildings'):
        quarter = 'DISTRICT_CSC_'+key+'_QUARTER'
        quarters[quarter] = key
        if stage in (2, 3, 4): add(customer, quarter, 'ordinary:'+str(stage))
    for quarter, customer in db.execute('SELECT SellerDistrictType,CustomerDistrictType FROM CSC_Stage3CustomerTransactions'):
        add(customer, quarter, 'population:3')
        if quarter.startswith('DISTRICT_CSC_') and quarter.endswith('_QUARTER'):
            quarters[quarter] = quarter[len('DISTRICT_CSC_'):-len('_QUARTER')]
    # Exact Wonder buyers use a building-placement consumer. Record their
    # gameplay definitions explicitly; a generic DISTRICT_WONDER adjacency
    # would incentivise every Wonder, including unrelated ones.
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='CSC_QuarterWonderSales'").fetchone():
        for key, building, stage in db.execute('SELECT QuarterKey,BuildingType,ProducerStage FROM CSC_QuarterWonderSales'):
            if stage in (2,3,4):
                excluded.append(dict(customer='DISTRICT_WONDER',quarter='DISTRICT_CSC_'+key+'_QUARTER',
                                     source='exact-wonder:'+str(stage),building=building))
    tags = defaultdict(set)
    for district, tag in db.execute('SELECT Type,Tag FROM TypeTags'):
        tags[tag].add(district)
    for quarter, key in quarters.items():
        for suffix, source in (('SALES','sales-tag'),('GOODS_PROVIDER','goods-provider')):
            for customer in tags['CLASS_CSC_'+key+'_'+suffix]:
                add(customer, quarter, source)
    base = list(expected.items())
    for unique, parent in db.execute('SELECT CivUniqueDistrictType,ReplacesDistrictType FROM DistrictReplaces'):
        for (customer, quarter), sources in base:
            if customer == parent and unique in districts:
                expected[(unique, quarter)].update('replacement:'+s for s in sources)
    actual, duplicates = {}, []
    for customer, quarter, amount, tiles in db.execute('''
SELECT d.DistrictType,a.AdjacentDistrict,a.YieldChange,a.TilesRequired
FROM District_Adjacencies d JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId
WHERE a.YieldType='YIELD_CSC_AI_PLACEMENT' '''):
        if (customer,quarter) in actual: duplicates.append([customer,quarter])
        actual[(customer, quarter)] = dict(amount=amount, tiles=tiles)
    missing = sorted(set(expected)-set(actual))
    extra = sorted(set(actual)-set(expected))
    invalid = [dict(customer=c,quarter=q,**r)for (c,q),r in actual.items()
               if r['amount']<=0 or r['tiles']!=1]
    return dict(complete=not(missing or extra or invalid or duplicates), expected=len(expected), actual=len(actual),
        missing=[dict(customer=c,quarter=q,sources=sorted(expected[(c,q)]))for c,q in missing],
        unexpected=[dict(customer=c,quarter=q)for c,q in extra], invalid=invalid, duplicates=duplicates, excluded=excluded,
        edges=[dict(customer=c,quarter=q,sources=sorted(s),native=actual.get((c,q)))
               for (c,q),s in sorted(expected.items())])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    args = parser.parse_args()
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro', uri=True)) as db:
        print(json.dumps(audit(db), indent=2))
