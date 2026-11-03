"""Verify live mapped-resource coverage without changing tested forecast paths."""
import json
PRIVATE='YIELD_CSC_AI_PLACEMENT'
MOD='MOD_CSC_AI_MAPPED_IMPROVEMENT_'
REQ='REQ_CSC_AI_MAPPED_IMPROVEMENT_'
SET='REQSET_CSC_AI_MAPPED_IMPROVEMENT_'
TAGS=('CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC','CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC')

def mapped_pairs(db):
 return set(db.execute('SELECT DISTINCT v.ImprovementType,v.ResourceType FROM Improvement_ValidResources v JOIN Resources r ON r.ResourceType=v.ResourceType JOIN TypeTags t ON t.Type=r.ResourceType WHERE t.Tag IN (?,?,?,?)',TAGS))

def existing_early(db,typ,resource):
 flat=list(db.execute('SELECT YieldChange FROM Improvement_YieldChanges WHERE ImprovementType=? AND YieldType=?',(typ,PRIVATE)))
 if flat:
  assert flat==[(80,)],('Unexpected existing direct forecast',typ,flat)
  return 'existing_direct80'
 rows=list(db.execute("SELECT m.ModifierType,m.OwnerRequirementSetId FROM ImprovementModifiers i JOIN Modifiers m ON m.ModifierId=i.ModifierId WHERE i.ImprovementType=? AND i.ModifierId='MOD_CSC_AI_FARM_RESOURCE_FORECAST'",(typ,)))
 if rows:
  assert len(rows)==1 and rows[0][0]=='MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS'
  assert dict(db.execute("SELECT Name,Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_AI_FARM_RESOURCE_FORECAST'"))=={'YieldType':PRIVATE,'Amount':'80'}
  reqset=rows[0][1];assert list(db.execute('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?',(reqset,)))==[('REQUIREMENTSET_TEST_ANY',)]
  matches=list(db.execute("SELECT r.RequirementType FROM RequirementSetRequirements s JOIN Requirements r ON r.RequirementId=s.RequirementId JOIN RequirementArguments a ON a.RequirementId=r.RequirementId WHERE s.RequirementSetId=? AND a.Name='ResourceType' AND a.Value=?",(reqset,resource)))
  if matches:
   assert all(x[0]=='REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES'for x in matches)
   return 'existing_resource_Farm80'
 return None

def verify_loaded(db,base):
 pairs=mapped_pairs(db);assert pairs and pairs==mapped_pairs(base),'Native mappings changed'
 groups={};coverage=[]
 for typ,resource in sorted(pairs):
  path=existing_early(db,typ,resource)
  if path is None:groups.setdefault(typ,set()).add(resource);path='new_resource_conditional80'
  coverage.append(dict(improvement=typ,resource=resource,path=path,early_private80=True))
 assert {tuple(x)for x in db.execute("SELECT ImprovementType,ModifierId FROM ImprovementModifiers WHERE ModifierId GLOB 'MOD_CSC_AI_MAPPED_IMPROVEMENT_*'")}=={(typ,MOD+typ)for typ in groups}
 for typ,resources in groups.items():
  assert list(db.execute('SELECT ModifierType,OwnerRequirementSetId FROM Modifiers WHERE ModifierId=?',(MOD+typ,)))==[('MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',SET+typ)]
  assert dict(db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?',(MOD+typ,)))=={'YieldType':PRIVATE,'Amount':'80'}
  assert list(db.execute('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?',(SET+typ,)))==[('REQUIREMENTSET_TEST_ANY',)]
  assert {x[0]for x in db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',(SET+typ,))}=={REQ+r for r in resources}
  for resource in resources:
   assert list(db.execute('SELECT RequirementType FROM Requirements WHERE RequirementId=?',(REQ+resource,)))==[('REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES',)]
   assert dict(db.execute('SELECT Name,Value FROM RequirementArguments WHERE RequirementId=?',(REQ+resource,)))=={'ResourceType':resource}
 # Only the new requirement/modifier rows may change. Native legality, ordinary
 # yields, existing early paths, adjacent signals, care and worker policy match.
 allowed={'Requirements','RequirementArguments','RequirementSets','RequirementSetRequirements','Modifiers','ModifierArguments','ImprovementModifiers'}
 tables=[x[0]for x in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")];changed=[]
 assert set(tables)=={x[0]for x in base.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
 for table in tables:
  rows=lambda con:sorted(json.dumps(list(x),default=str)for x in con.execute('SELECT * FROM "'+table+'"'))
  before,after=rows(base),rows(db)
  if before!=after:
   assert table in allowed and set(before)<=set(after),('Unexpected DB change',table)
   changed.append(table)
 return dict(verified=True,mapped_pairs=len(pairs),coverage=coverage,new_conditional_resources={k:sorted(v)for k,v in groups.items()},changed_tables=sorted(changed),terrain_or_unmapped_new_bonus=0,existing_forecast_adjacent_care_worker_paths_unchanged=True,all_owner_diagnostic=True,native_application_and_decision_response='PENDING native evidence')
