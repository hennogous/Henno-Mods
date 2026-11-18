"""Compile real population declarations/consumers without launching Civ.

Only native schema and vanilla building locations are fixtures. Transaction
identities, terms, properties, bits and modifier graphs come from actual SQL.
The optional reference directory is the pre-migration source snapshot; it is
used once for full graph/Lua parity and is never copied into shipping content.
"""
from pathlib import Path
import re
import sqlite3

ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'Civ Supply Chains'
NATIVE={'DistrictModifiers','BuildingModifiers','Modifiers','ModifierArguments',
        'RequirementSets','RequirementSetRequirements','Requirements','RequirementArguments'}


def statements(text):
    # SQL strings in this slice contain neither comment delimiters nor semicolons.
    text=re.sub(r'/\*.*?\*/|--[^\n]*','',text,flags=re.S)
    return [s.strip()+';'for s in text.split(';')if s.strip()]


def matches_population(text):
    return bool(re.search(r'(?:MOD|REQSET|REQ)_CSC_(?:BAKERS|TAILORS)_(?:MARKET_(?:RETURN|FOOD)|CUSTOMER_RETURN|(?:MARKET|TEMPLE)_CUSTOMER_CULTURE)',text)
        or re.search(r'(?:MOD|REQSET|REQ)_CSC_(?:BAKERS|TAILORS)_STAGE_4_.*?(?:RETURN|Branch)',text,re.S)
        or 'CSC_BakersStage4CultureBuildings'in text)


def fixed_aliases():
    # Alias IDs come from the actual declarations, not another interaction list.
    aliases=set()
    for q in ('BAKERS','TAILORS'):
        for suffix in ('','_GOLD'):
            source=(MOD/f'Data/CSC_Q_{q}{suffix}.sql').read_text()
            for statement in statements(source):
                if not re.match(r'INSERT INTO CSC_BuildingTransactionFixedBindings\b',statement):continue
                aliases.update(x for x in re.findall(r"'((?:MOD|REQSET|REQ)_CSC_[A-Z0-9_]+)'",statement)
                    if not x.endswith('_BIT_'))
    return aliases


def material_aliases():
    aliases=set()
    for q in('BAKERS','TAILORS'):
        for kind in('','_MC_MODE'):
            for suffix in('','_GOLD'):
                for statement in statements((MOD/f'Data/CSC_Q_{q}{kind}{suffix}.sql').read_text(encoding='utf-8-sig')):
                    if re.match(r'INSERT INTO CSC_MaterialTransaction(?:Gate)?Bindings\b',statement):
                        aliases.update(re.findall(r"'((?:MOD|REQSET|REQ)_CSC_[A-Z0-9_]+)'",statement))
    return aliases


def route_aliases():
    aliases=set()
    for q in ('BAKERS','TAILORS'):
        for suffix in ('','_GOLD'):
            for statement in statements((MOD/f'Data/CSC_Q_{q}{suffix}.sql').read_text()):
                if re.match(r'INSERT INTO CSC_TradeRoute\w+\b',statement):
                    aliases.update(re.findall(r"'(MOD_CSC_[A-Z0-9_]+)'",statement))
    return aliases


def compile_catalogue(*,gold=True,lgd=True,reference=None,uniques=False,mc=False,source_root=None):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.executescript('''
CREATE TABLE Buildings(BuildingType TEXT PRIMARY KEY, PrereqDistrict TEXT, IsWonder INTEGER DEFAULT 0);
CREATE TABLE BuildingReplaces(CivUniqueBuildingType TEXT, ReplacesBuildingType TEXT);
CREATE TABLE Building_CitizenYieldChanges(BuildingType TEXT,YieldType TEXT,YieldChange INTEGER,PRIMARY KEY(BuildingType,YieldType));
CREATE TABLE ImprovementModifiers(ImprovementType TEXT, ModifierId TEXT, UNIQUE(ImprovementType,ModifierId));
CREATE TABLE DistrictModifiers(DistrictType TEXT, ModifierId TEXT, UNIQUE(DistrictType,ModifierId));
CREATE TABLE BuildingModifiers(BuildingType TEXT, ModifierId TEXT, UNIQUE(BuildingType,ModifierId));
CREATE TABLE Modifiers(ModifierId TEXT PRIMARY KEY, ModifierType TEXT, OwnerRequirementSetId TEXT, SubjectRequirementSetId TEXT, RunOnce INTEGER DEFAULT 0, Permanent INTEGER DEFAULT 0, OwnerStackLimit INTEGER, SubjectStackLimit INTEGER, NewOnly INTEGER DEFAULT 0, Repeatable INTEGER DEFAULT 0);
CREATE TABLE DynamicModifiers(ModifierType TEXT PRIMARY KEY,CollectionType TEXT,EffectType TEXT);
INSERT INTO DynamicModifiers VALUES
 ('MODIFIER_SINGLE_CITY_ADJUST_PROPERTY','COLLECTION_OWNER','EFFECT_ADJUST_CITY_PROPERTY'),
 ('MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE','COLLECTION_OWNER','EFFECT_ADJUST_CITY_YIELD_CHANGE'),
 ('MODIFIER_BUILDING_YIELD_CHANGE','COLLECTION_OWNER','EFFECT_ADJUST_BUILDING_YIELD_CHANGE');
CREATE TABLE ModifierArguments(ModifierId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(ModifierId,Name));
CREATE TABLE RequirementSets(RequirementSetId TEXT PRIMARY KEY,RequirementSetType TEXT);
CREATE TABLE RequirementSetRequirements(RequirementSetId TEXT,RequirementId TEXT,PRIMARY KEY(RequirementSetId,RequirementId));
CREATE TABLE Requirements(RequirementId TEXT PRIMARY KEY,RequirementType TEXT,Inverse INTEGER DEFAULT 0);
CREATE TABLE RequirementArguments(RequirementId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(RequirementId,Name));
''')
    locations={'MARKET':'COMMERCIAL_HUB','TEMPLE':'HOLY_SITE','ZOO':'ENTERTAINMENT_COMPLEX',
        'FERRIS_WHEEL':'WATER_ENTERTAINMENT_COMPLEX','AMPHITHEATER':'THEATER','GRANARY':'CITY_CENTER','LIGHTHOUSE':'HARBOR',
        'BOLSHOI_THEATRE':'WONDER','BROADWAY':'WONDER','SYDNEY_OPERA_HOUSE':'WONDER'}
    if lgd:locations['LEU_CONSERVATORY']='LEU_GARDEN'
    for q,buildings in {'BAKERS':['WATER_MILL','WIND_MILL','BAKERY','CAFE'],'TAILORS':['TEXTILE_WORKSHOP','TAILOR','FASHION_HOUSE']}.items():
        for b in buildings:locations['CSC_'+q+'_'+b]='CSC_'+q+'_QUARTER'
    db.executemany('INSERT INTO Buildings VALUES(?,?,?)',[
        ('BUILDING_'+b,'DISTRICT_'+d,int(d=='WONDER'))for b,d in locations.items()])
    if uniques:
        for name,district in [('GRANARY','CITY_CENTER'),('LIGHTHOUSE','HARBOR')]:
            db.execute('INSERT INTO Buildings VALUES(?,?,0)',('BUILDING_UNIQUE_'+name,'DISTRICT_'+district))
            db.execute('INSERT INTO BuildingReplaces VALUES(?,?)',('BUILDING_UNIQUE_'+name,'BUILDING_'+name))
    source=Path(source_root or reference or MOD)
    consolidated=(source/'Data/CSC_Q_ALL_Schema.sql').exists()
    # source_root permits a before/after consolidation comparison through the
    # SAME native loader. reference retains the older pre-migration semantics.
    schema_source=source if not reference else MOD
    if consolidated or reference:
        db.executescript((schema_source/'Data/CSC_Q_ALL_Schema.sql').read_text(encoding='utf-8-sig'))
    else:
        for filename in ('CSC_BuildingTransactionSchema.sql','CSC_TradeRouteSchema.sql'):
            db.executescript((source/'Data'/filename).read_text(encoding='utf-8-sig'))
    shared=(source/('Data/CSC_Q_ALL_Common.sql'if consolidated else'Data/CSC_Q_ALL.sql')).read_text(encoding='utf-8-sig')
    names={'CSC_QuarterFlowBuildings','CSC_QuarterCustomerBuildings','CSC_QuarterWonderSales','CSC_QuarterWonderServices','CSC_Stage3CustomerTransactions',
        'CSC_ScaledAmountBits','CSC_Stage3RateBits','CSC_Stage4StackBits','CSC_RouteStackBits'}
    for s in statements(shared):
        if any(re.match(r'(?:CREATE TABLE IF NOT EXISTS|INSERT OR IGNORE INTO)\s+'+n+r'\b',s)for n in names)or re.match(r'INSERT(?: OR IGNORE)? INTO DynamicModifiers\b',s):db.executescript(s)
    files=['Data/CSC_Q_BAKERS.sql','Data/CSC_Q_TAILORS.sql']
    if gold:files+=['Data/CSC_Q_BAKERS_GOLD.sql','Data/CSC_Q_TAILORS_GOLD.sql']
    if mc:
        for q in('BAKERS','TAILORS'):
            files.append(f'Data/CSC_Q_{q}_MC_MODE.sql')
            if gold:files.append(f'Data/CSC_Q_{q}_MC_MODE_GOLD.sql')
    if lgd:files+=['ModSupport/ModSupport_LGD.sql']
    # Load every native INSERT, independent of whether its VALUES neighbours
    # happen to mention a transaction alias. Cleanup can legitimately remove
    # those neighbours without removing the remaining Service or route gates.
    for f in files:
        text=(source/f).read_text(encoding='utf-8-sig')
        # Read by table/dependency, not by a declaration section's old position.
        # Economic terms now precede native plumbing. The temporary venue and
        # import tables still execute with all their dependent SELECTs in order.
        for s in statements(text):
            table=re.match(r'INSERT(?: OR IGNORE)? INTO (\w+)',s)
            if ('CSC_BakersStage4CultureBuildings'in s or
                re.search(r'CSC_(?:Bakers|Tailors)Import(?:Channels|Effects)\b',s)or
                (table and table[1]in (NATIVE|{'ImprovementModifiers'}))or
                (table and table[1]in names|{'Building_CitizenYieldChanges'})):
                db.executescript(s)
    if not reference:
        # Economic declarations now live in their Quarter/Gold/MC files. Read
        # only declarations here: native structures above remain independently
        # selected, so loading a whole Quarter cannot hide a missing generator.
        declarations=files if consolidated else [
            *[f'Data/CSC_Q_{q}_TRANSACTIONS{suffix}.sql'for q in ('BAKERS','TAILORS')for suffix in (('','_GOLD')if gold else('',))],
            *[f for f in files if '_MC_MODE'in f or f.startswith('ModSupport/')]]
        for relative in declarations:
            for s in statements((source/relative).read_text(encoding='utf-8-sig')):
                if re.match(r'INSERT(?: OR IGNORE)? INTO CSC_(?:BuildingTransaction|MaterialTransaction|TradeRoute)\w*\b',s):
                    db.executescript(s)
        processors=('CSC_Q_ALL_TransactionProcessor.sql','CSC_Q_ALL_TradeRouteReader.sql')if consolidated else(
            'CSC_MaterialTransactionProcessor.sql','CSC_FixedBuildingTransactionProcessor.sql',
            'CSC_BuildingTransactionProcessor.sql','CSC_TradeRouteProcessor.sql')
        for filename in processors:db.executescript((source/'Data'/filename).read_text())
    return db


def graph(db,scope='population'):
    aliases=fixed_aliases()if scope=='fixed'else material_aliases()if scope=='material'else set()
    def include(table,row):
        identity=row[1]if table in('BuildingModifiers','DistrictModifiers','ImprovementModifiers')else row[0]
        if scope=='all_csc':return identity.startswith(('MOD_CSC_','REQ_CSC_','REQSET_CSC_'))
        return matches_population(identity)if scope=='population'else identity in aliases
    tables=NATIVE|{'ImprovementModifiers'}if scope=='material'else NATIVE
    return {n:sorted([list(r)for r in db.execute('SELECT * FROM '+n)if include(n,r)],key=repr)for n in sorted(tables)}


def legacy_reference_graph(db,scope='population'):
    """Compare historical eight-column fixture hashes without rewriting evidence.

    NewOnly/Repeatable were absent from the original reduced native schema. Assert
    both are zero before projecting its original column order; raw graph() still
    retains every native column for current comparisons and live qualification.
    """
    result=graph(db,scope)
    columns=[r[1]for r in db.execute('PRAGMA table_info(Modifiers)')]
    original=('ModifierId','ModifierType','OwnerRequirementSetId','SubjectRequirementSetId',
              'RunOnce','Permanent','OwnerStackLimit','SubjectStackLimit')
    for row in result['Modifiers']:
        assert all(not row[columns.index(name)]for name in ('NewOnly','Repeatable'))
    result['Modifiers']=[[row[columns.index(name)]for name in original]for row in result['Modifiers']]
    return result


def bind_population(vm):
    """Supply the real catalogue to older game-object-only lifecycle fixtures."""
    db=compile_catalogue()
    for name in ('CSC_BuildingTransactions','CSC_BuildingTransactionYields'):
        rows=[dict(r)for r in db.execute('SELECT * FROM '+name)]
        records=vm.table_from([vm.table_from(row)for row in rows])
        if name=='CSC_BuildingTransactions':
            for i,row in enumerate(rows,1):records[row['TransactionId']]=records[i]
        vm.globals().CSC_POPULATION_TEST_ROWS=records
        vm.execute('''local rows=CSC_POPULATION_TEST_ROWS
GameInfo['''+repr(name)+''']=setmetatable(rows,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})''')
    for row in db.execute('SELECT * FROM Buildings'):
        definition=vm.globals().GameInfo.Buildings[row['BuildingType']]
        if definition is not None:
            definition.PrereqDistrict=row['PrereqDistrict'];definition.IsWonder=row['IsWonder']
    db.close()
