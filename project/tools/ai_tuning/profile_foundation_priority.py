"""Read-only native input checks; neither callback registration nor inputs prove efficacy."""
def validate_database(db):
 rows=[]
 for q in ('BAKERS','TAILORS'):
  strategy='STRATEGY_CSC_RH_FINISH_'+q;name='CSC_RH_Finish_'+q
  assert db.execute('SELECT Kind FROM Types WHERE Type=?',(strategy,)).fetchone()==('KIND_VICTORY_STRATEGY',)
  assert db.execute('SELECT VictoryType,NumConditionsNeeded FROM Strategies WHERE StrategyType=?',(strategy,)).fetchone()==(None,1)
  assert db.execute('SELECT System FROM AiLists WHERE ListType=?',(name,)).fetchone()==('Districts',)
  assert db.execute('SELECT 1 FROM Strategy_Priorities WHERE StrategyType=? AND ListType=?',(strategy,name)).fetchone()
  assert db.execute("SELECT StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=? AND ConditionFunction='Call Lua Function'",(strategy,)).fetchone()==(name,0)
  assert db.execute("SELECT Disqualifier FROM StrategyConditions WHERE StrategyType=? AND ConditionFunction='Is Not Major'",(strategy,)).fetchone()==(1,)
  assert db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?',(name,)).fetchall()==[('DISTRICT_CSC_'+q+'_QUARTER',1,300)]
  rows.append(dict(quarter=q,strategy=strategy,list=name,value=300))
 reverse=0;forward=0
 for candidate,neighbor,value in db.execute("SELECT d.DistrictType,a.AdjacentDistrict,a.YieldChange FROM District_Adjacencies d JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId WHERE a.ID LIKE 'CSC_AI_SALES_%'"):
  is_quarter=candidate.startswith('DISTRICT_CSC_')and candidate.endswith('_QUARTER')
  assert value==(10 if is_quarter else 30),(candidate,neighbor,value)
  if is_quarter:forward+=1
  else:
   assert candidate!='DISTRICT_CITY_CENTER'and neighbor.startswith('DISTRICT_CSC_')
   reverse+=1
 assert forward>0 and reverse>0
 return dict(verified_inputs=True,strategies=rows,forward_edges=forward,reverse_edges=reverse,forward_value=10,reverse_value=30,native_choice_effect='UNPROVEN',scope='player-wide Quarter type while confirmed original assisted backlog exists')
