"""Load real native route read-models into a Lua game-object fixture."""
from functools import lru_cache
from population_catalogue_fixture import compile_catalogue,MOD

TABLES=('CSC_TradeRouteChannels','CSC_TradeRouteChannelFacts','CSC_TradeRouteSupplyRequirements',
        'CSC_TradeRoutePayoutBindings','CSC_TradeRoutePayouts')


@lru_cache(maxsize=2)
def rows(gold=True):
    db=compile_catalogue(gold=gold)
    result={name:[dict(r)for r in db.execute('SELECT * FROM '+name)]for name in TABLES}
    db.close();return result


def bind(vm,*,gold=True,database=None):
    data=rows(gold)if database is None else{name:[dict(r)for r in database.execute('SELECT * FROM '+name)]for name in TABLES}
    vm.globals().CSC_ROUTE_TEST_ROWS=vm.table_from({name:vm.table_from([vm.table_from(r)for r in values])for name,values in data.items()})
    vm.execute('''
GameInfo=GameInfo or{}
include=include or function()end
for name,values in pairs(CSC_ROUTE_TEST_ROWS)do
 local records=values
 GameInfo[name]=function()local i=0;return function()i=i+1;return records[i]end end
end
if GameInfo.Buildings then
 local index=0
 for _,v in pairs(GameInfo.Buildings)do if type(v)=='table'and v.Index then index=math.max(index,v.Index+1)end end
 for _,channel in ipairs(CSC_ROUTE_TEST_ROWS.CSC_TradeRouteChannels)do
  if not GameInfo.Buildings[channel.ProducerBuildingType]then
   local row={Index=index,BuildingType=channel.ProducerBuildingType}
   GameInfo.Buildings[index]=row;GameInfo.Buildings[row.BuildingType]=row;index=index+1
  end
 end
end
''')
    for name in ('CSC_TradeRouteCore.lua','CSC_TradeRouteFacts.lua'):
        vm.execute((MOD/'Lua_UI/TradeRoutes'/name).read_text(encoding='utf-8'))


def copy_read_model(database):
    """Provide the real late projection to independent native/UI SQL fixtures."""
    database.executescript((MOD/'Data/CSC_TradeRouteSchema.sql').read_text())
    for name,values in rows().items():
        if not values:continue
        columns=list(values[0])
        database.executemany('INSERT INTO '+name+'('+','.join(columns)+') VALUES('+','.join('?'for _ in columns)+')',
                             [[row[c]for c in columns]for row in values])
