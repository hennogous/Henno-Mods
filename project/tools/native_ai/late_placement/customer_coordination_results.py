"""Join physical customer links to both directions of CSC placement guidance.

Closed-log analysis only. Exact proposed footprints, native private-yield
readings and later physical links are separate fields; co-occurrence is not
labelled a controlled causal effect. Uses maintained planning chronology.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import re

from planning_results import parse


def fields(text):
    result={}
    for key,value in re.findall(r'(\w+)=([^\s]+)',text):
        try:result[key]=float(value)if'.'in value else int(value)
        except ValueError:result[key]=value
    return result


def physical_summary(links):
    # Keep owner-specific evidence rows for receipt attribution, but count a
    # physical Quarter/neighbour pair once when conquest changes its owner.
    # One district beside two Quarters still supplies two economic links.
    pairs=defaultdict(list)
    for row in links:
        pairs[(row['quarter'],row['quarterPlot'],row['customerDistrict'],row['customerPlot'])].append(row)
    eligible=[rows for rows in pairs.values()if not rows[0]['cityCenter']]
    orders=Counter()
    for rows in eligible:
        values={row['order']for row in rows}
        orders[next(iter(values))if len(values)==1 else'conflicting_history']+=1
    return dict(physical_links=len(pairs),planned_district_links=len(eligible),
        city_center_links=len(pairs)-len(eligible),order=dict(orders),
        owner_scoped_links=len(links),owner_scoped_planned_links=sum(not r['cityCenter']for r in links),
        exact_prior_customer_first_links=sum(any(r['exactPriorCustomerFirstLink']for r in rows)for rows in eligible),
        latest_quarter_layout_matches=sum(any(r['latestQuarterLayoutMatches']for r in rows)for rows in eligible),
        links_with_prior_economic_offer=sum(any(r['priorCustomerEconomicOffer']for r in rows)for rows in eligible),
        customer_foundations_with_private_yield=len({(r['customerDistrict'],r['customerPlot'])
            for r in links if not r['cityCenter']and(r['privateYieldAtCustomerFoundation']or 0)>0}),
        existing_quarter_links_observed_without_base=sum(any(r['ownedBaseAtCustomerPlacement']==0 for r in rows)for rows in eligible))


def district_breakdown(links,constructions,types,mapped):
    # The frozen loaded SQL connector registry supplies zero-link district
    # types too. This avoids omitting Harbors simply because no pair formed.
    founded=Counter(types.get(r['district'],str(r['district']))for r in constructions)
    result={}
    for kind in sorted({r['customerDistrict']for r in links}|(set(founded)&mapped)):
        rows=[r for r in links if r['customerDistrict']==kind]
        result[kind]=dict(foundations=founded[kind],
            adjacent_district_sites=len({r['customerPlot']for r in rows}),
            quarter_district_pairs=len({(r['quarter'],r['quarterPlot'],r['customerPlot'])for r in rows}),
            customer_placed_after_quarter=len({r['customerPlot']for r in rows if r['order']=='quarter_first'}),
            roles=sorted({role for r in rows for role in r['roles']}))
    return result


def analyse(root):
    root=Path(root)
    detailed=json.loads((root/'planning-results.json').read_text())
    log=(root/'Lua.log').read_text(encoding='utf-8-sig')
    catalogue=(root/'loaded-district-catalogue.txt').read_text(encoding='utf-8-sig').replace('\0','')
    types={int(i):name for i,name in re.findall(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t([^\t\r\n]+)',catalogue)}
    constructions={(r['player'],r['district'],r['plot']):r for r in detailed['constructions']}
    future=[fields(s)for s in re.findall(r'CSC_AI_CUSTOMER_FUTURE_LINK ([^\r\n]+)',log)]
    layouts=[fields(s)for s in re.findall(r'CSC_AI_SPATIAL_BID ([^\r\n]+)',log)]
    economic=[fields(s)for s in re.findall(r'CSC_AI_CUSTOMER_ECONOMIC_BID ([^\r\n]+)',log)]
    material=defaultdict(list)
    for row in parse(log,'CSC_PLANNING_'):
        if row['kind']=='MATERIAL_STATE':material[(row['player'],row['quarterPlot'])].append(row)
    pairs={}
    for row in detailed['relationship_pairs']:
        if row.get('present'):
            key=(row['player'],row['quarterPlot'],row['neighbourPlot'])
            if key not in pairs:pairs[key]=dict(row,roles=set())
            pairs[key]['roles'].add(row['role'])
    result=[]
    for (pid,qplot,cplot),edge in sorted(pairs.items()):
        customer_type=edge['neighbourDistrict'];qtype='DISTRICT_CSC_'+edge['quarter']+'_QUARTER'
        qindex=next((i for i,name in types.items()if name==qtype),None)
        customer=constructions.get((pid,customer_type,cplot),{})
        qt,ct=edge.get('quarterFoundationTurn'),edge.get('neighbourFoundationTurn')
        if qt is None or ct is None:order='unknown'
        elif qt<ct:order='quarter_first'
        elif ct<qt:order='customer_first'
        else:order='same_turn'
        # A prior offer must precede its proposed district's recorded foundation.
        reverse=[r for r in future if r.get('player')==pid and r.get('plot')==cplot
                 and r.get('district')==customer_type and r.get('quarterPlot')==qplot
                 and r.get('quarterDistrict')==qindex and ct is not None and r['turn']<=ct]
        quotes=[r for r in layouts if r.get('player')==pid and r.get('plot')==qplot
                and r.get('district')==qindex and qt is not None and r['turn']<=qt]
        latest=max(quotes,key=lambda r:r['turn'])if quotes else None
        planned=bool(latest and any(latest.get('customerPlot'+str(i))==cplot
            and latest.get('customerType'+str(i))==customer_type for i in (1,2)))
        econ=[r for r in economic if r.get('player')==pid and r.get('plot')==cplot
              and r.get('district')==customer_type and ct is not None and r['turn']<=ct]
        eco=max(econ,key=lambda r:r['turn'])if econ else None
        # Latest observed supplier facts at/before customer placement. Customer-
        # first links have no existing-Quarter inventory yet, so stay unknown.
        states={}
        if qt is not None and ct is not None and qt<=ct:
            for r in sorted(material[(pid,qplot)],key=lambda r:(r['turn'],r.get('sequence',0))):
                if r['turn']<=ct:states[r['materialPlot']]=r
        bases=[r for r in states.values()if r.get('base')and r.get('owner')==pid and r.get('district',-1)<0]
        private=customer.get('uiAdjacency',{}).get('YIELD_CSC_AI_PLACEMENT')
        result.append(dict(player=pid,quarter=edge['quarter'],quarterPlot=qplot,
            customerPlot=cplot,customerDistrict=types.get(customer_type,str(customer_type)),
            quarterTurn=qt,customerTurn=ct,order=order,roles=sorted(edge['roles']),
            cityCenter=types.get(customer_type)=='DISTRICT_CITY_CENTER',
            privateYieldAtCustomerFoundation=private,
            exactPriorCustomerFirstLink=bool(reverse),customerFirstLastTurn=max((r['turn']for r in reverse),default=None),
            latestQuarterLayoutMatches=planned,quarterLayoutTurn=latest['turn']if latest else None,
            priorCustomerEconomicOffer=bool(econ),economicLastTurn=eco['turn']if eco else None,
            economicLastDeltaQ8=eco.get('deltaQ8')if eco else None,
            baseInventoryObserved=bool(states),ownedBaseAtCustomerPlacement=len(bases)if states else None,
            workingBaseAtCustomerPlacement=sum(bool(r.get('working')and r.get('compatible'))for r in bases)if states else None))
    summary=physical_summary(result)
    database=root/'loaded-native-customer-database.json'
    mapped={r['DistrictType']for r in json.loads(database.read_text())['links']}if database.is_file()else set()
    gaps=[fields(s)for s in re.findall(r'CSC_AI_CUSTOMER_ECONOMIC_GAPS ([^\r\n]+)',log)]
    return dict(schema='csc-customer-coordination-v2',summary=summary,links=result,
        district_placements=district_breakdown(result,detailed['constructions'],types,mapped),
        diagnostics=dict(skip_totals={key:sum(r.get(key,0)for r in gaps)for key in
            ('referenceUnavailable','candidateUnavailable','nativeUnavailable','nativeNonpositive','unvisitedGroups')}),
        scope='Physical counts deduplicate ownership changes; evidence links retain player identity. Layout logging covers the leading two Quarter offers only.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();data=analyse(args.run)
    args.output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data['summary'],indent=2))
