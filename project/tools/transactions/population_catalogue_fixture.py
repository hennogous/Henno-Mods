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


def compile_catalogue(*,gold=True,lgd=True,reference=None):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.executescript('''
CREATE TABLE Buildings(BuildingType TEXT PRIMARY KEY, PrereqDistrict TEXT, IsWonder INTEGER DEFAULT 0);
CREATE TABLE DistrictModifiers(DistrictType TEXT, ModifierId TEXT, UNIQUE(DistrictType,ModifierId));
CREATE TABLE BuildingModifiers(BuildingType TEXT, ModifierId TEXT, UNIQUE(BuildingType,ModifierId));
CREATE TABLE Modifiers(ModifierId TEXT PRIMARY KEY, ModifierType TEXT, OwnerRequirementSetId TEXT, SubjectRequirementSetId TEXT, RunOnce INTEGER DEFAULT 0, Permanent INTEGER DEFAULT 0, OwnerStackLimit INTEGER, SubjectStackLimit INTEGER);
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
    shared=(MOD/'Data/CSC_Q_ALL.sql').read_text(encoding='utf-8-sig')
    names={'CSC_QuarterFlowBuildings','CSC_QuarterCustomerBuildings','CSC_QuarterWonderSales','CSC_Stage3CustomerTransactions',
        'CSC_ScaledAmountBits','CSC_Stage3RateBits','CSC_Stage4StackBits'}
    for s in statements(shared):
        if any(re.match(r'(?:CREATE TABLE IF NOT EXISTS|INSERT OR IGNORE INTO)\s+'+n+r'\b',s)for n in names):db.executescript(s)
    source=Path(reference)if reference else MOD
    files=['Data/CSC_Q_BAKERS.sql','Data/CSC_Q_TAILORS.sql']
    if gold:files+=['Data/CSC_Q_BAKERS_GOLD.sql','Data/CSC_Q_TAILORS_GOLD.sql']
    if lgd:files+=['ModSupport/ModSupport_LGD.sql']
    # Populate pre-existing consumers and their full requirements/attachments.
    # Mixed VALUES statements are retained whole, so the comparison includes
    # their neighboring definitions too rather than hiding an accidental edit.
    for f in files:
        for s in statements((source/f).read_text(encoding='utf-8-sig')):
            table=re.match(r'INSERT(?: OR IGNORE)? INTO (\w+)',s)
            if ('CSC_BakersStage4CultureBuildings'in s or
                (table and table[1]in NATIVE and matches_population(s))or
                (table and table[1]in names)):
                db.executescript(s)
    if not reference:
        db.executescript((MOD/'Data/CSC_BuildingTransactionSchema.sql').read_text())
        for q in ['BAKERS','TAILORS']:
            db.executescript((MOD/f'Data/CSC_Q_{q}_TRANSACTIONS.sql').read_text())
            if gold:db.executescript((MOD/f'Data/CSC_Q_{q}_TRANSACTIONS_GOLD.sql').read_text())
        if lgd:
            for s in statements((MOD/'ModSupport/ModSupport_LGD.sql').read_text(encoding='utf-8-sig')):
                if re.match(r'INSERT INTO CSC_BuildingTransaction',s):db.executescript(s)
        db.executescript((MOD/'Data/CSC_BuildingTransactionProcessor.sql').read_text())
    return db


def graph(db):
    return {n:sorted([list(r)for r in db.execute('SELECT * FROM '+n)],key=repr)for n in sorted(NATIVE)}
