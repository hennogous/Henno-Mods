"""Stage 4 rows, effect graphs, text, UI consumers and executable Lua gates."""
from pathlib import Path
import importlib.util
import re
import sqlite3
import unittest
import io
import json
import yaml



def validate_service_slot_notifications(texts, prefix, citizen_slots, district_name):
    """Keep persistent building slots separate from stackable service effects."""
    failures = []
    for state in ('NEW', 'INCREASED', 'DECREASED', 'REMOVED'):
        fragment = texts.get(prefix + '_' + state, '')
        if citizen_slots and state == 'NEW':
            slot = f'+{citizen_slots} [ICON_Citizen] Citizen slot in the {district_name}'
            if slot not in fragment:
                failures.append(prefix + ': NEW must state ' + slot)
        elif citizen_slots and state == 'REMOVED':
            if 'The established service and its [ICON_Citizen] Citizen slot remain' not in fragment:
                failures.append(prefix + ': REMOVED must state that the service and Citizen slot remain')
        elif '[ICON_Citizen] Citizen slot' in fragment:
            failures.append(prefix + ': ' + state + ' must not imply a new, stacked or removed Citizen slot')
    return failures


def validate(root, db, implementation):
    failures=[]
    def expect(actual, expected, label):
        if actual!=expected:failures.append(f'{label}: expected {expected!r}, found {actual!r}')
    def one(sql,*values):
        row=db.execute(sql,values).fetchone();return None if row is None else row[0]
    def arguments(modifier):
        return dict(db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?',(modifier,)))
    def members(sid):
        return {r[0] for r in db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',(sid,))}
    design=yaml.safe_load((root/'project/specs/tailors/design.yaml').read_text())
    building=next(b for b in design['buildings'] if b['id']=='D.STAGE4')
    effects={e['id']:e for e in building['effects']}
    fashion=building['type'];service=effects['D.STAGE4.SERVICE']['service']
    expect(db.execute('SELECT PrereqCivic,Cost,Maintenance,PrereqDistrict,CitizenSlots,Entertainment,RegionalRange FROM Buildings WHERE BuildingType=?',(fashion,)).fetchone(),(building['prerequisite'],building['cost'],building['maintenance_gold'],'DISTRICT_CSC_TAILORS_QUARTER',effects['D.STAGE4.SPECIALISTS']['citizen_slots'],effects['D.STAGE4.REGIONAL_AMENITY']['amenities'],effects['D.STAGE4.REGIONAL_AMENITY']['radius']),'Fashion House definition')
    expect(one('SELECT PrereqBuilding FROM BuildingPrereqs WHERE Building=?',fashion),building['prerequisite_building'],'Fashion House prerequisite')
    expect(dict(db.execute('SELECT YieldType,YieldChange FROM Building_CitizenYieldChanges WHERE BuildingType=?',(fashion,))),effects['D.STAGE4.SPECIALISTS']['citizen_yields'],'Fashion House specialists')
    for yield_type,suffix in [('YIELD_PRODUCTION','PROD'),('YIELD_GOLD','GOLD')]:
        mid='MOD_CSC_TAILORS_FASHION_HOUSE_'+suffix+'_TO_WORKSHOP'
        expect(arguments(mid),{'BuildingType':'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','YieldType':yield_type,'Amount':'1'},'Fashion House local sender '+suffix)
        expect(one('SELECT BuildingType FROM BuildingModifiers WHERE ModifierId=?',mid),fashion,'Fashion House owns local return '+suffix)
    expect(one("SELECT BuildingType FROM BuildingModifiers WHERE ModifierId='MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE'"),'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','Workshop owns Fashion House Culture')
    for suffix,total in [('IMPROVEMENT',1),('INDUSTRY',2),('CORPORATION',3)]:
        leaf='MOD_CSC_TAILORS_SPEC_'+('' if suffix=='IMPROVEMENT' else suffix+'_')+'CULTURE_TO_FASHION_HOUSE'
        wrapper='MOD_CSC_TAILORS_SPEC_'+suffix+'_ATTACH_QUARTER'
        expect(arguments(leaf),{'BuildingType':fashion,'YieldType':'YIELD_CULTURE','Amount':str(total)},'Fashion House Specialty '+suffix+' total')
        expect(arguments(wrapper).get('ModifierId'),leaf,'Specialty '+suffix+' effect graph')
        expect(db.execute('SELECT OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(wrapper,)).fetchone(),('REQSET_CSC_TAILORS_PLOT_HAS_SPEC','REQSET_CSC_ADJ_TAILORS_QUARTER'),'Specialty '+suffix+' gate')
        expected={'IMPROVEMENT_PLANTATION','IMPROVEMENT_MINE'} if suffix=='IMPROVEMENT' else {'IMPROVEMENT_'+suffix}
        expect({r[0] for r in db.execute('SELECT ImprovementType FROM ImprovementModifiers WHERE ModifierId=?',(wrapper,))},expected,'Specialty '+suffix+' sources')

    # Every binary consumer targets the receiving building and is independently
    # attached to City Center, with no material gate on population transactions.
    binding=next(r for p in implementation['phases'] if p['id']=='stage4' for r in p['requirements'] if r['id']=='I.STAGE_MANAGER')['wonder_service_binding']
    variants=binding['wonder_variants']
    customers=[('AMPHITHEATER','BUILDING_AMPHITHEATER')]+[(v['service_building_type'].rsplit('_',1)[1],v['host_wonder_type']) for v in variants]
    targets=[('FASHION_HOUSE_RETURN',fashion,'YIELD_PRODUCTION'),('FASHION_HOUSE_RETURN',fashion,'YIELD_GOLD')]+[(branch+'_CULTURE_RETURN',host,'YIELD_CULTURE') for branch,host in customers]
    bits=[r[0] for r in db.execute('SELECT Bit FROM CSC_Stage4StackBits ORDER BY Bit')]
    expect(bits,[1<<i for i in range(20)],'Stage 4 SQL/Lua integer bit vocabulary')
    for branch,target,yield_type in targets:
        for bit in bits:
            mid=f'MOD_CSC_TAILORS_STAGE_4_{branch}_{yield_type[6:]}_BIT_{bit}'
            sid=f'REQSET_CSC_TAILORS_STAGE_4_{branch}_BIT_{bit}'
            expect(arguments(mid),{'BuildingType':target,'YieldType':yield_type,'Amount':str(bit)},mid+' arguments')
            expect(db.execute('SELECT ModifierType,OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(mid,)).fetchone(),('MODIFIER_BUILDING_YIELD_CHANGE',None,sid),mid+' gate')
            expect(one('SELECT COUNT(*) FROM DistrictModifiers WHERE DistrictType=? AND ModifierId=?','DISTRICT_CITY_CENTER',mid),1,mid+' attachment')
            property_name=one("SELECT RA.Value FROM RequirementSetRequirements RSR JOIN RequirementArguments RA ON RA.RequirementId=RSR.RequirementId WHERE RSR.RequirementSetId=? AND RA.Name='PropertyName'",sid)
            expect(property_name,f'CSC_TAILORS_STAGE_4_{branch}_BIT_{bit}',mid+' property')

    expect(members('REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ'),{'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE','REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC'},'Stage 4 Base AND Specialty supply')
    expect(members('REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ'),{'REQ_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ','REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET'},'shared non-circular producer eligibility')
    expect(members('REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ'),{'REQ_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ','REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER'},'Stage Manager complete activation gate reuses producer eligibility')
    for branch in ('SUPPLY','PRODUCER'):
        req='REQ_CSC_TAILORS_STAGE_4_'+branch+'_PREREQ'
        sid='REQSET_CSC_TAILORS_STAGE_4_'+branch+'_PREREQ'
        expect(db.execute('SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId=?',(req,)).fetchone(),('REQUIREMENT_REQUIREMENTSET_IS_MET',0),'nested Stage4 '+branch+' requirement')
        expect(one("SELECT Value FROM RequirementArguments WHERE RequirementId=? AND Name='RequirementSetId'",req),sid,'nested Stage4 '+branch+' target')
        expect(one('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?',sid),'REQUIREMENTSET_TEST_ALL','Stage4 '+branch+' AND gate')
    bridge='MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY'
    expect(one('SELECT BuildingType FROM BuildingModifiers WHERE ModifierId=?',bridge),fashion,'Fashion House owns SQL service eligibility property')
    expect(db.execute('SELECT ModifierType,OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(bridge,)).fetchone(),('MODIFIER_SINGLE_CITY_ADJUST_PROPERTY','REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',None),'SQL service eligibility uses shared producer gate without customer readiness')
    expect(arguments(bridge),{'Key':'CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE','Amount':'1'},'SQL service eligibility property output')
    wonder_source=(root/'Civ Supply Chains/Lua_UI/WonderServices/CSC_WonderServicePlacement.lua').read_text()
    expect('CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE' in wonder_source,True,'Wonder placement consumes SQL source eligibility')
    expect(any(token in wonder_source for token in ('HasCivic(', 'CSC_TAILORS_FASHION_HOUSE_SUPPLIED', 'CIVIC_OPERA_BALLET')),False,'Wonder placement has no duplicate unlock/material rule')
    expect(one("SELECT Value FROM RequirementArguments WHERE RequirementId='REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET' AND Name='CivicType'"),effects['D.STAGE4.SERVICE']['unlock'],'Stage Manager civic')
    expect(members('REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'),{'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER','REQ_CSC_TAILORS_DISTRICT_IS_THEATER','REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER'},'normal service destination')
    expect(one("SELECT Value FROM RequirementArguments WHERE RequirementId='REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER' AND Name='MustBeFunctioning'"),'1','functioning Amphitheater')
    expect(db.execute('SELECT PrereqDistrict,MustPurchase,CitizenSlots,Cost,Maintenance FROM Buildings WHERE BuildingType=?',(service,)).fetchone(),('DISTRICT_THEATER',1,1,0,0),'normal Stage Manager')
    expect(arguments('MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT'),{'BuildingType':service},'normal persistent SQL grant')
    expect(db.execute("SELECT OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId='MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER'").fetchone(),('REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ','REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'),'normal grant shares producer/effect gate')
    for v in variants:
        expect(db.execute('SELECT PrereqDistrict,MustPurchase,CitizenSlots,Cost,Maintenance,Name FROM Buildings WHERE BuildingType=?',(v['service_building_type'],)).fetchone(),('DISTRICT_WONDER',1,0,0,0,'LOC_'+v['service_building_type']+'_NAME'),'Wonder Stage Manager '+v['host_wonder_type'])
        expect(one("SELECT COUNT(*) FROM ModifierArguments MA JOIN Modifiers M ON M.ModifierId=MA.ModifierId WHERE MA.Name='BuildingType' AND MA.Value=? AND M.ModifierType LIKE '%GRANT_BUILDING%'",v['service_building_type']),0,'no SQL grant for '+v['host_wonder_type'])
        expect(one('SELECT Pillage FROM Buildings_XP2 WHERE BuildingType=?',v['service_building_type']),0,'Wonder service cannot be pillaged')
    expect(arguments('MOD_CSC_TAILORS_STAGE_MANAGER_GPP'),{'GreatPersonClassType':'GREAT_PERSON_CLASS_ARTIST','Amount':'1'},'Stage Manager Artist point')
    art_modifier='MOD_CSC_TAILORS_STAGE_4_ART_PROPERTY'
    expect(one('SELECT BuildingType FROM BuildingModifiers WHERE ModifierId=?',art_modifier),fashion,'Fashion House owns Stage4 art state')
    expect(db.execute('SELECT ModifierType,OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(art_modifier,)).fetchone(),('MODIFIER_SINGLE_CITY_ADJUST_PROPERTY','REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',None),'Stage4 art source shares complete Service gate')
    expect(arguments(art_modifier),{'Key':'CSC_TAILORS_STAGE_4_EFFECT_TOURISM','Amount':'1'},'Stage4 art source arguments')
    anchors=[]
    for venue in ('','BOLSHOI','BROADWAY','SYDNEY'):
        suffix='_'+venue if venue else ''
        subject='REQSET_CSC_TAILORS_ADJ_STAGE_4_'+venue if venue else 'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'
        child='MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM'+suffix
        expect(arguments(child),{'Amount':str(effects['D.STAGE4.SERVICE']['effects']['city_tourism_boost'])},'Stage Manager Tourism '+venue)
        expect(one('SELECT ModifierType FROM Modifiers WHERE ModifierId=?',child),'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE','flat destination district Tourism '+venue)
        if venue:
            expect(members(subject),{'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER','REQ_CSC_TAILORS_STAGE_4_'+venue+'_READY'},'exact Wonder subject gate '+venue)
        for kind in ('TOURISM','GPP'):
            mid='MOD_CSC_TAILORS_STAGE_MANAGER_'+kind+'_ATTACH_'+(venue or 'CUSTOMER')
            expect(one('SELECT BuildingType FROM BuildingModifiers WHERE ModifierId=?',mid),fashion,'Stage Manager seller-owned source '+kind+suffix)
            expect(db.execute('SELECT OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(mid,)).fetchone(),('REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',subject),'Stage Manager effects gate '+kind+suffix)
            expect(arguments(mid).get('ModifierId'),child if kind=='TOURISM' else 'MOD_CSC_TAILORS_STAGE_MANAGER_GPP','Stage Manager graph '+kind+suffix)
        anchors.append(('MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_'+(venue or 'CUSTOMER'),child,effects['D.STAGE4.SERVICE']['effects']['city_tourism_boost'],'ICON_'+service+suffix,service+suffix,'TAILORS',*['LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'+suffix+state for state in ('','_NEW','_INCREASED','_DECREASED','_REMOVED')]))
    actual=db.execute("SELECT ModifierId,AbilityEffectModifierId,AbilityArgumentAmount,AbilityIcon,AbilityIconTarget,NotificationQuarter,AbilityDesc,AbilityNewDesc,AbilityIncreasedDesc,AbilityDecreasedDesc,AbilityRemovedDesc FROM CSC_AbilityAttachModifiers WHERE ModifierId LIKE 'MOD_CSC_TAILORS_STAGE_MANAGER_%'").fetchall()
    expect(sorted(actual),sorted(anchors),'four real venue-specific Stage Manager presentation anchors')
    expect(one("SELECT COUNT(*) FROM BuildingModifiers WHERE ModifierId LIKE 'MOD_CSC_TAILORS_STAGE_MANAGER_%_ATTACH_%'"),8,'one Tourism and one GPP wrapper per venue, no aggregate double attachment')

    for suffix,yield_type,building_target in [('CULTURE','YIELD_CULTURE',None),('PRODUCTION','YIELD_PRODUCTION',fashion),('GOLD','YIELD_GOLD',fashion)]:
        mid='MOD_CSC_TAILORS_'+('IMPORT' if suffix=='CULTURE' else 'EXPORT')+'_FASHION_HOUSE_'+suffix
        expect(arguments(mid).get('Amount'),'1','Stage 4 trade '+suffix+' amount')
        expect(arguments(mid).get('YieldType'),yield_type,'Stage 4 trade '+suffix+' yield')
        if building_target:expect(arguments(mid).get('BuildingType'),building_target,'Stage 4 trade seller target '+suffix)
    expect(arguments('MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY'),{'Amount':'1'},'Stage 4 trade origin Amenity')
    expect(one("SELECT COUNT(*) FROM CSC_TradeRouteYieldPresentation WHERE EntryId='CSC_TAILORS_IMPORT_SPECIALTY_CULTURE' AND ModifierId='MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE' AND PropertyName='CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE' AND YieldType='YIELD_CULTURE' AND Amount=1"),1,'Stage 4 outgoing trade presentation registry')

    # Generate/check the actual text database, including raw integration SQL.
    text_db=sqlite3.connect(':memory:')
    text_db.execute('CREATE TABLE LocalizedText (Language TEXT,Tag TEXT,Text TEXT,PRIMARY KEY(Language,Tag))')
    try:
        text_db.executescript((root/'Civ Supply Chains/Text/CSC_TAILORS_TEXT.sql').read_text(encoding='utf-8-sig'))
        texts=dict(text_db.execute("SELECT Tag,Text FROM LocalizedText WHERE Language='en_US'"))
        desc=texts.get('LOC_'+fashion+'_DESCRIPTION','')
        positions=[desc.find(token) for token in ('Specialty Materials improvement','local Textile Workshop','per 5 [ICON_Citizen] Citizens','incoming [ICON_TradeRoute]','At Opera and Ballet')]
        expect(all(i>=0 for i in positions) and positions==sorted(positions),True,'Fashion House description order')
        expect(any(token in desc for token in ('Citizen slot','[ICON_Amenities] Amenity within','Industry','Corporation')),False,'engine stats and M&C omitted from base description')
        for target,history_count in [(fashion,3),(service,1),*[(v['service_building_type'],1) for v in variants]]:
            prefix='LOC_PEDIA_BUILDINGS_PAGE_'+target+'_CHAPTER_'
            expect({tag[len(prefix):] for tag in texts if tag.startswith(prefix)},{'CSCHAIN_TITLE','CSCHAIN_PARA_1','HISTORY_TITLE',*[f'HISTORY_PARA_{i}' for i in range(1,history_count+1)]},target+' Cafe-style Pedia chapter structure')
            expect(texts.get(prefix+'HISTORY_TITLE'),'Historical Context',target+' Historical Context title')
        for target in effects['D.STAGE4.POP_CUSTOMERS']['customers']+['BUILDING_MARAE']:
            paragraph=texts.get('LOC_PEDIA_BUILDINGS_PAGE_'+target+'_CHAPTER_CSCHAIN_PARA_1','')
            expect(all(term in paragraph for term in ('Fashion House','population', 'LOC_'+next((v['service_building_type'] for v in variants if v['host_wonder_type']==target),service)+'_NAME')),True,target+' integrated customer Pedia')
        for target in ['DISTRICT_THEATER','DISTRICT_ACROPOLIS']:
            expect('LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME' in texts.get('LOC_PEDIA_DISTRICTS_PAGE_'+target+'_CHAPTER_CSCHAIN_PARA_1',''),True,target+' service pointer')
        for suffix, expected_name in [('', 'Stage Manager'), ('_BOLSHOI', 'Ballet Dancer'), ('_BROADWAY', 'Musical Actor'), ('_SYDNEY', 'Opera Singer')]:
            expect(texts.get('LOC_'+service+suffix+'_NAME'), expected_name, 'distinct service name '+suffix)
            expect('+2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist]' in texts.get('LOC_'+service+suffix+'_DESCRIPTION',''),True,'service Tourism description '+suffix)
        for venue in ('','BOLSHOI','BROADWAY','SYDNEY'):
            suffix='_'+venue if venue else ''
            citizen_slots=one('SELECT CitizenSlots FROM Buildings WHERE BuildingType=?',service+suffix)
            failures.extend(validate_service_slot_notifications(texts,'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'+suffix,citizen_slots,'Theater Square'))
            preview=texts.get('LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'+suffix,'')
            expect(preview.startswith('{LOC_'+service+suffix+'_NAME}:'),True,'MCUIS service label has canonical name only '+venue)
            for state in ('NEW','INCREASED','DECREASED','REMOVED'):
                fragment=texts.get('LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'+suffix+'_'+state,'')
                expect(bool(fragment),True,'Stage Manager notification '+venue+' '+state)
                expect('[ICON_Tourism] Tourism' in fragment and '% [ICON_Culture]' not in fragment,True,'flat Tourism notification '+venue+' '+state)
                expect('LOC_'+service+suffix+'_NAME' in fragment,True,'venue service notification name '+venue+' '+state)
                expect(bool(re.search(r'\{LOC_'+service+suffix+r'_NAME\}(?:\s+service)?\s+(?:at|on|in)\b',fragment)),False,'notification service label has no venue suffix '+venue+' '+state)
                expect(bool(re.search(r'[+-]\s*\{[12]_',fragment)),False,'MCUIS signs dynamic amounts '+venue+' '+state)
        text_db.executescript((root/'Civ Supply Chains/Text/CSC_TAILORS_MC_MODE_TEXT.sql').read_text(encoding='utf-8-sig'))
        mc_desc=text_db.execute('SELECT Text FROM LocalizedText WHERE Tag=?',('LOC_'+fashion+'_DESCRIPTION',)).fetchone()[0]
        expect('Industry' in mc_desc and 'Corporation' in mc_desc,True,'conditional Fashion House M&C text')
    except sqlite3.DatabaseError as exc:failures.append('Stage 4 localization integration: '+str(exc))
    finally:text_db.close()

    for relative in ('CSC_WonderServicePlotTooltip_Base.lua','CSC_WonderServicePlotTooltip_Suk.lua'):
        source=(root/'Civ Supply Chains/Lua_UI/WonderServices'/relative).read_text()
        expect('data.BuildingTypes' in source,True,relative+' actual plot buildings')
        expect('BUILDING_ORACLE' in source or 'HOSTING_SPIKE' in source,False,relative+' laboratory identifiers absent')
    city_ui=(root/'Civ Supply Chains/Lua_UI/WonderServices/CSC_WonderServiceCityBreakdown.lua').read_text()
    expect('GetBuildingsAtLocation' in city_ui,True,'City Breakdown actual plot location API')
    expect('GetBuildingLocation(' in city_ui,False,'City Breakdown does not call unavailable gameplay location API')
    manifest=json.loads((root/'project/modbuddy/CivSupplyChains.actions.json').read_text())
    bts_actions=[a for a in manifest['blocks']['inGameActions'] if a.get('id')=='CSC_BTS_TradeRouteSupport']
    expect(len(bts_actions),1,'BTS preview shared import action')
    if bts_actions:
        expect('Lua_UI/TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua' in bts_actions[0].get('files',[]),True,'BTS preview source included by shared import')
    for name in ('CSC_WonderServiceCityBreakdown','CSC_TradeRouteInteractions'):
        xml=(root/'Civ Supply Chains/Lua_UI'/('WonderServices' if name.startswith('CSC_Wonder') else 'TradeRoutes')/(name+'.xml'))
        expect(xml.with_suffix('.lua').is_file(),True,name+' paired UI context script')
    for icon,index in [('ICON_'+fashion,6)]+[('ICON_'+service+suffix,index) for suffix,index in (('',12),('_BOLSHOI',13),('_BROADWAY',14),('_SYDNEY',15))]:
        source=(root/'Civ Supply Chains/Icons/CSC_TAILORS_ICONS.sql').read_text()
        expect(bool(re.search(r"\(\s*'"+icon+r"'\s*,\s*'ICON_ATLAS_CSC_TAILORS'\s*,\s*"+str(index)+r'\s*\)',source)),True,icon+' atlas index')

    # These tests execute the shipped Lua. Missing Lupa or a failed scenario is a
    # real readiness failure, never a skipped green phase.
    path=root/'project/tools/quarter_contracts/tests/test_fashion_house_gameplay.py'
    try:
        spec=importlib.util.spec_from_file_location('csc_fashion_house_tests',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromModule(module))
        if not result.wasSuccessful():failures.append('Fashion House executable Lua scenarios:\n'+stream.getvalue())
    except (ImportError,OSError) as exc:failures.append('Fashion House Lua scenario dependency: '+str(exc))
    return failures
