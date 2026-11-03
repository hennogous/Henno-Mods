"""Read-only native preflight for the reviewed RH strategy counterpart inputs.

This checks authored inputs before autoplay, not strategy adoption, native score
arithmetic or eventual production. No game connection or mutation is performed.
"""
PRODUCERS=('BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP')
CONSUMERS=('BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_TAILORS_TAILOR')
VENUES=('BUILDING_CSC_BAKERS_CAFE','BUILDING_CSC_TAILORS_FASHION_HOUSE')
TEMPLATES={'RHDevZoneBuildings':[(PRODUCERS,'BUILDING_WORKSHOP'),(CONSUMERS,'BUILDING_FACTORY'),(VENUES,'BUILDING_BROADCAST_CENTER')],
 'IndustrialBuildings':[(PRODUCERS,'BUILDING_WORKSHOP'),(CONSUMERS,'BUILDING_FACTORY')],
 **{name:[(PRODUCERS+CONSUMERS,'BUILDING_FACTORY')] for name in ('ModernBuildings','AtomicBuildings','InformationBuildings')}}

def validate_database(db):
 """Fail closed on a mismatch in this explicitly opted-in RH5 experiment.

 The reviewed RH5 source has no authored CSC counterpart entries. A future RH
 release with its own entries needs a separate review, rather than silently
 treating a changed native preference as this experiment's verified input.
 """
 assert db.execute("SELECT Mode FROM CSC_AI_Profile WHERE Id='ACTIVE'").fetchone()==('RH',),'Strategy controls require RH profile'
 rows=[]
 for name,groups in TEMPLATES.items():
  assert db.execute("SELECT COUNT(*)FROM AiLists WHERE ListType=? AND System='Buildings'",(name,)).fetchone()[0]==1,name
  assert db.execute('SELECT COUNT(*)FROM Strategy_Priorities WHERE ListType=?',(name,)).fetchone()[0]>0,name
  for targets,template in groups:
   sources=db.execute('SELECT * FROM AiFavoredItems WHERE ListType=? AND Item=?',(name,template)).fetchall()
   assert len(sources)==1,(name,template,'native source ambiguity')
   source=sources[0]
   for target in targets:
    expected=(name,target,*source[2:])
    actual=db.execute('SELECT * FROM AiFavoredItems WHERE ListType=? AND Item=?',(name,target)).fetchall()
    assert actual==[expected],(name,target,'counterpart preference mismatch')
    rows.append(dict(list=name,template=template,item=target,favored=source[2],value=source[3],source_metadata=list(source[4:])))
 assert len(rows)==27
 return dict(verified=True,native_counterpart_rows=rows,rows=len(rows),
  evidence='Native database preference input only; strategy adoption and production outcomes require their own logs and physical readbacks.')
