"""Check native sales/bonus/river tuning against a read-only native DB copy."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib

ROOT = Path(__file__).resolve().parents[3]
LIST = 'CSC_AI_ImprovementPriorities'


def inventory(db):
    return {name: hashlib.sha256(repr(sorted(db.execute('SELECT * FROM "'+name+'"').fetchall(),key=repr)).encode()).hexdigest()
            for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database', type=Path, default=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite")
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--loaded', action='store_true')
    a = p.parse_args()
    source = sqlite3.connect(a.database.as_uri()+'?mode=ro', uri=True)
    db = sqlite3.connect(':memory:')
    source.backup(db)
    source.close()
    # Cached schema triggers call the engine function. This local surrogate is
    # for SQL validation only; the real game supplies its native hash function.
    db.create_function('Make_Hash',1,lambda value:zlib.crc32(value.encode()))
    before = inventory(db)
    if not a.loaded:
        # A prior disposable prototype may be the last native cache. Rebuild its
        # owned adjacency rows in this in-memory copy, as a fresh game does.
        db.execute("DELETE FROM District_Adjacencies WHERE YieldChangeId LIKE 'CSC_AI_SALES_%'")
        db.execute("DELETE FROM District_Adjacencies WHERE YieldChangeId LIKE 'CSC_AI_MATERIAL_%'")
        db.execute("DELETE FROM District_Adjacencies WHERE YieldChangeId IN ('CSC_AI_BONUS_RESOURCE','CSC_AI_RIVER')")
        db.execute("DELETE FROM Adjacency_YieldChanges WHERE YieldType='YIELD_CSC_AI_PLACEMENT'")
        db.executescript((ROOT/'Civ Supply Chains/Data/CSC_AI.sql').read_text())
    assert not db.execute('SELECT 1 FROM AiLists WHERE ListType=?',(LIST,)).fetchall()
    assert not db.execute('SELECT 1 FROM AiFavoredItems WHERE ListType=?',(LIST,)).fetchall()
    assert db.execute("SELECT LeaderType,System FROM AiLists WHERE ListType='UnitPriorityBoosts'").fetchall()==[('TRAIT_LEADER_MAJOR_CIV','Units')]
    assert db.execute("SELECT Favored,Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall()==[(1,50)]
    changed = sorted(name for name, digest in inventory(db).items() if before.get(name) != digest)
    allowed = {'PseudoYields','AiFavoredItems','AiListTypes','AiLists','Types','Yields','Technologies','TechnologyPrereqs',
               'Technologies_XP2','Requirements','RequirementSets','RequirementSetRequirements','RequirementArguments',
               'Modifiers','ModifierArguments','TraitModifiers','Adjacency_YieldChanges','District_Adjacencies','DistrictModifiers'}
    assert not set(changed)-allowed, changed
    assert not a.loaded or not changed, changed
    if a.loaded:
        assert not db.execute("SELECT * FROM Technologies WHERE TechnologyType='TECH_CSC_AI_PLACEMENT'").fetchall()
    assert db.execute("SELECT DefaultValue FROM Yields WHERE YieldType='YIELD_CSC_AI_PLACEMENT'").fetchone() == (1,)
    edges = db.execute("SELECT a.DistrictType,y.AdjacentDistrict,y.YieldChange,y.PrereqTech FROM District_Adjacencies a JOIN Adjacency_YieldChanges y ON a.YieldChangeId=y.ID WHERE y.ID LIKE 'CSC_AI_SALES_%'").fetchall()
    assert edges and len(edges) == len(set(edges))
    assert all(e[2:] == (10,None) for e in edges)
    assert not any(e[0]=='DISTRICT_CITY_CENTER' for e in edges)
    assert ('DISTRICT_CSC_TAILORS_QUARTER','DISTRICT_ROYAL_NAVY_DOCKYARD',10,None) in edges
    assert ('DISTRICT_ROYAL_NAVY_DOCKYARD','DISTRICT_CSC_TAILORS_QUARTER',10,None) in edges
    guidance=db.execute("SELECT a.DistrictType,y.ID,y.YieldChange,y.TilesRequired,y.AdjacentResourceClass,y.AdjacentRiver,y.AdjacentFeature,y.YieldType FROM District_Adjacencies a JOIN Adjacency_YieldChanges y ON y.ID=a.YieldChangeId WHERE y.ID IN ('CSC_AI_BONUS_RESOURCE','CSC_AI_RIVER')").fetchall()
    quarters={'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'}
    variants=quarters|{r[0] for r in db.execute('SELECT CivUniqueDistrictType FROM DistrictReplaces WHERE ReplacesDistrictType IN (?,?)',tuple(sorted(quarters)))}
    assert len(guidance)==2*len(variants) and len(guidance)==len(set(guidance)),guidance
    for district,key,amount,tiles,resource,river,feature,yield_type in guidance:
        assert district in variants and tiles==1 and feature is None and yield_type=='YIELD_CSC_AI_PLACEMENT'
        if key=='CSC_AI_BONUS_RESOURCE':assert (amount,resource,river)==(12,'RESOURCECLASS_BONUS',0)
        else:assert (amount,resource,river)==(4,'NO_RESOURCECLASS',1)
    assert not db.execute("SELECT * FROM ModifierArguments WHERE Name='YieldTypeToMirror' AND Value='YIELD_CSC_AI_PLACEMENT'").fetchall()
    assert not db.execute("SELECT * FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%'").fetchall()
    assert not db.execute("SELECT * FROM Adjacency_YieldChanges WHERE ID LIKE 'CSC_AI_MATERIAL_%'").fetchall()
    sql=(ROOT/'Civ Supply Chains/Data/CSC_AI.sql').read_text()
    assert 'INSERT OR IGNORE INTO Features' not in sql
    supply=db.execute("SELECT d.DistrictType,m.ModifierId,m.ModifierType,m.OwnerRequirementSetId,m.SubjectRequirementSetId FROM DistrictModifiers d JOIN Modifiers m USING(ModifierId) WHERE m.ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%'").fetchall()
    expected=db.execute("SELECT DISTINCT d.DistrictType,r.ResourceType FROM Districts d JOIN TypeTags t ON t.Tag IN (CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_BASE' ELSE 'CLASS_CSC_TAILORS_BASE' END,CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_SPEC' ELSE 'CLASS_CSC_TAILORS_SPEC' END) JOIN Resources r ON r.ResourceType=t.Type WHERE d.DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER')").fetchall()
    assert len(supply)==2*len(expected) and len(supply)==len(set(supply))
    for quarter,resource in expected:
        for stage,amount in [('PRESENT',40),('IMPROVED',80)]:
            mid='MOD_CSC_AI_SUPPLY_'+quarter+'__'+resource+'_'+stage
            expected_args=[('Amount',str(amount)),('YieldType','YIELD_CSC_AI_PLACEMENT')] if stage=='PRESENT' else [('ModifierId','MOD_CSC_AI_SUPPLY_IMPROVED_VALUE')]
            assert db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=? ORDER BY Name',(mid,)).fetchall()==expected_args
    assert all(row[2]==('MODIFIER_PLAYER_ADJUST_PLOT_YIELD' if row[1].endswith('_PRESENT') else 'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER') and row[3]=='REQSET_CSC_AI_SUPPLY_AI' for row in supply)
    assert db.execute("SELECT ModifierType FROM Modifiers WHERE ModifierId='MOD_CSC_AI_SUPPLY_IMPROVED_VALUE'").fetchone()==('MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',)
    assert db.execute("SELECT Name,Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_AI_SUPPLY_IMPROVED_VALUE' ORDER BY Name").fetchall()==[('Amount','80'),('YieldType','YIELD_CSC_AI_PLACEMENT')]
    once = inventory(db)
    db.executescript((ROOT/'Civ Supply Chains/Data/CSC_AI.sql').read_text())
    assert inventory(db) == once, 'Repeated component creates duplicate rows'
    # Check the relevant references explicitly. The base cache has pre-existing
    # unrelated FK violations; this validator never suppresses SQL failures.
    assert db.execute("SELECT 1 FROM Traits WHERE TraitType='TRAIT_LEADER_MAJOR_CIV'").fetchone()
    default = db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0]
    assert default == 90, default
    result = {'status': 'passed', 'loaded_native_database': a.loaded, 'changed_tables': changed,
              'supply_modifiers': len(supply), 'supply_present': 40, 'supply_improved_extra': 80, 'global_improvement_default': default, 'reapplication_identical': True,
              'ai_list': 'UnitPriorityBoosts', 'item': 'UNIT_BUILDER', 'value': 50, 'own_improvement_bias_removed': True,
              'sales_edges': len(edges), 'sales_strength': 10,
              'guidance_edges': len(guidance), 'bonus_resource_strength': 12, 'river_strength': 4,
              'exact_material_guidance': False, 'specialty_strength': 0,
              'sql_sha256': hashlib.sha256((ROOT/'Civ Supply Chains/Data/CSC_AI.sql').read_bytes()).hexdigest()}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
