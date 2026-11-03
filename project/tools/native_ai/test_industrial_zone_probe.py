"""Source-gate failures must prevent any AI advancement or instrumentation."""
import copy
import unittest
import industrial_zone_probe as probe

class SourceGateTests(unittest.TestCase):
 def fixture(self):
  def target(player,city,workshop):
   x,y,plot=(52,40,3160)if player==4 else(46,18,1304)
   return dict(player=player,city=city,exists=True,alive=True,human=False,major=True,
    x=x,y=y,technologies={'TECH_INDUSTRIALIZATION':True},districts=[dict(complete=True,pillaged=False,plot=plot)],
    workshop=dict(present=workshop,pillaged=False),factory=dict(present=False))
  return dict(turn=250,player0=dict(human=True,alive=True),mapping=dict(workshopIndex=23,factoryIndex=24,buildingIndexLimit=25,buildingCount=25),targets=[target(4,262147,False),target(2,589832,True)],relevantDB=dict(buildings=[dict(type='BUILDING_WORKSHOP',tech='TECH_APPRENTICESHIP',district='DISTRICT_INDUSTRIAL_ZONE',placement=False),dict(type='BUILDING_FACTORY',tech='TECH_INDUSTRIALIZATION',district='DISTRICT_INDUSTRIAL_ZONE',placement=False)],prerequisites=[dict(building='BUILDING_FACTORY',prerequisite='BUILDING_WORKSHOP')]))
 def test_original_two_contrasting_targets(self):self.assertTrue(probe.validate_source(self.fixture()))
 def test_human_or_dead_target_rejected(self):
  for key,value in [('human',True),('alive',False),('exists',False),('major',False)]:
   with self.subTest(key=key):
    f=self.fixture();f['targets'][0][key]=value
    with self.assertRaises(ValueError):probe.validate_source(f)
 def test_missing_tech_or_pillaged_iz_rejected(self):
  f=self.fixture();f['targets'][0]['technologies']['TECH_INDUSTRIALIZATION']=False
  with self.assertRaises(ValueError):probe.validate_source(f)
  f=self.fixture();f['targets'][0]['districts'][0]['pillaged']=True
  with self.assertRaises(ValueError):probe.validate_source(f)
 def test_prerequisite_contrast_required(self):
  for target,present,pillaged in [(0,True,False),(1,False,False),(1,True,True)]:
   f=self.fixture();f['targets'][target]['workshop'].update(present=present,pillaged=pillaged)
   with self.assertRaises(ValueError):probe.validate_source(f)
 def test_wrong_clock_observer_or_mapping_rejected(self):
  fs=[]
  f=self.fixture();f['turn']=251;fs.append(f)
  f=self.fixture();f['player0']['human']=False;fs.append(f)
  f=self.fixture();f['mapping']['buildingCount']=24;fs.append(f)
  f=self.fixture();f['mapping']['factoryIndex']=23;fs.append(f)
  for f in fs:
   with self.assertRaises(ValueError):probe.validate_source(f)
 def test_complete_factory_or_wrong_pair_rejected(self):
  f=self.fixture();f['targets'][1]['factory']['present']=True
  with self.assertRaises(ValueError):probe.validate_source(f)
 def test_wrong_city_coordinates_or_iz_site_rejected(self):
  f=self.fixture();f['targets'][0]['x']=53
  with self.assertRaises(ValueError):probe.validate_source(f)
  f=self.fixture();f['targets'][1]['districts'][0]['plot']=1305
  with self.assertRaises(ValueError):probe.validate_source(f)
  f=self.fixture();f['targets'][0]['city']=262148
  with self.assertRaises(ValueError):probe.validate_source(f)
 def test_duplicate_target_and_changed_native_prerequisite_rejected(self):
  f=self.fixture();f['targets'].append(copy.deepcopy(f['targets'][0]))
  with self.assertRaises(ValueError):probe.validate_source(f)
  f=self.fixture();f['relevantDB']['prerequisites']=[]
  with self.assertRaises(ValueError):probe.validate_source(f)

if __name__=='__main__':unittest.main()
