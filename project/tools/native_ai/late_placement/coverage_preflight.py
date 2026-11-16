"""Read the loaded DB to qualify material hosts and private provider adjacencies.

This is once-per-game observation, with no console or SQL writes. The rows
establish loaded coverage; physical transaction payouts remain separate evidence.
"""
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3

from driver import write_json
from customer_connector_audit import audit as audit_customers


ROOTS=(
 ('CLASS_CSC_BAKERS_BASE','MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'),
 ('CLASS_CSC_BAKERS_BASE','MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'),
 ('CLASS_CSC_BAKERS_SPEC','MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'),
 ('CLASS_CSC_TAILORS_BASE','MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'),
 ('CLASS_CSC_TAILORS_SPEC','MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'))


def inspect(database,output,*,require_complete=True):
    database=Path(database).resolve(strict=True)
    with closing(sqlite3.connect(database.as_uri()+'?mode=ro',uri=True))as db:
        expected=set()
        for tag,root in ROOTS:
            expected.update(db.execute('''SELECT DISTINCT v.ImprovementType,?
 FROM TypeTags t JOIN Resources r ON r.ResourceType=t.Type
 JOIN Improvement_ValidResources v ON v.ResourceType=t.Type
 JOIN Improvements i ON i.ImprovementType=v.ImprovementType
 WHERE t.Tag=? AND EXISTS(SELECT 1 FROM Modifiers WHERE ModifierId=?)
 AND i.ImprovementType NOT IN ('IMPROVEMENT_INDUSTRY','IMPROVEMENT_CORPORATION')''',(root,tag,root)))
        counts={pair:db.execute('SELECT COUNT(*) FROM ImprovementModifiers WHERE ImprovementType=? AND ModifierId=?',pair).fetchone()[0]
                for pair in sorted(expected)}
        # Read every registered Quarter/customer pair, including the separate
        # population-sales registry. A synthetic Stage3 row in the old catalogue
        # previously hid missing Hub/Holy Site signals. No parallel AI mapping
        # or fixed Quarter list belongs in this diagnostic.
        customers=audit_customers(db)
        providers={(r['customer'],r['quarter'])for r in customers['edges']
                   if any('goods-provider'in source for source in r['sources'])}
        links={pair:db.execute('''SELECT COUNT(*) FROM District_Adjacencies d
 JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId
 WHERE d.DistrictType=? AND a.AdjacentDistrict=? AND a.YieldType='YIELD_CSC_AI_PLACEMENT'
 AND a.YieldChange=1 AND a.TilesRequired=1''',pair).fetchone()[0]for pair in sorted(providers)}
    result=dict(database=str(database),database_sha256=hashlib.sha256(database.read_bytes()).hexdigest(),
        read_only=True,material_hosts=[dict(improvement=p[0],root=p[1],count=n)for p,n in counts.items()],
        provider_links=[dict(provider=p[0],quarter=p[1],count=n)for p,n in links.items()],
        customer_connectors=customers,
        verified=bool(counts)and customers['complete']and all(n==1 for n in (*counts.values(),*links.values())))
    write_json(Path(output)/'coverage-preflight.json',result)
    if require_complete and not result['verified']:
        raise AssertionError('Loaded material/customer/provider coverage incomplete; inspect coverage-preflight.json')
    return result
