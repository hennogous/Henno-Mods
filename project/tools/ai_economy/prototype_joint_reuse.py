"""Offline only: compare exact joint-search results with starting-world reuse.

Does not edit the main mod, frozen packages, or the active game's policy.
Logical evaluation/budget accounting remains identical. The reused world has
the same producer choices and disabled venues; prices/objectives are pure
functions of its facts, as required by the live publication's quote caches.
"""
import hashlib
import importlib.util
import json
import argparse
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-directory',type=Path,required=True,
    help='Explicit diagnostic output folder outside the source tree')
scratch=parser.parse_args().output_directory.resolve(strict=True)
assert not scratch.is_relative_to(ROOT),'Generated prototypes belong outside the source tree'
spec=importlib.util.spec_from_file_location('joint_tests',ROOT/'project/tools/ai_economy/test_joint_customer_economy.py')
tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
source=tests.MODEL.read_text(encoding='utf-8')
old='''                local chosen=selected[i]
                if #alternatives[i]>1 then for _,candidate in ipairs(alternatives[i])do
                    selected[i]=candidate
                    local result,error=evaluate(selected,disabled);if not result then return nil,error end'''
new='''                local chosen=selected[i]
                local startingChoice,startingResult=chosen,current
                if #alternatives[i]>1 then for _,candidate in ipairs(alternatives[i])do
                    selected[i]=candidate
                    local result,error
                    if candidate==startingChoice then
                        -- All other chain/venue choices are unchanged in this
                        -- coordinate. Reuse its exact starting world; count the
                        -- logical attempt so limits/failure semantics stay fixed.
                        evaluations=evaluations+1
                        if evaluations>limit then return nil,'Joint evaluation budget exceeded'end
                        result=startingResult
                    else result,error=evaluate(selected,disabled)end
                    if not result then return nil,error end'''
assert source.count(old)==1
prototype=scratch/'CSC_AI_EconomyModel_starting_reuse.lua'
prototype.write_text(source.replace(old,new),encoding='utf-8')
capture='''
__captured={};__priceCalls=0
local function canonical(v)
 if type(v)~='table'then
  if type(v)=='number'then return string.format('%.17g',v)end
  return type(v)..':'..tostring(v)
 end
 local keys={};for k in pairs(v)do keys[#keys+1]=k end
 table.sort(keys,function(a,b)return type(a)..tostring(a)<type(b)..tostring(b)end)
 local rows={};for _,k in ipairs(keys)do rows[#rows+1]=canonical(k)..'='..canonical(v[k])end
 return '{'..table.concat(rows,',')..'}'
end
local original=M.JointForecast
function M.JointForecast(w,p)
 local function counted(s,h)__priceCalls=__priceCalls+1;return p(s,h)end
 local r,e=original(w,counted)
 __captured[#__captured+1]=canonical(r)..' ERROR '..canonical(e)
 return r,e
end
'''
stress='''
for n=1,180 do
 local a,b=chain('A',1),chain('B',2)
 for i,s in ipairs({a,b})do
  s.seconds={{type='Wind',unlock=0,turns=1+n%4,terrain=n%3,maintenance=.5},
   {type='Water',unlock=0,turns=2,terrain=(n+i)%5,maintenance=1}}
  s.third={type='BAKERY',unlock=0,turns=1+n%5,maintenance=.2}
  if n%2==0 then s.fourth={type='CAFE',unlock=0,turns=2,maintenance=1}end
  s.customers={venue(100,3)};s.customers[1].maintenance=n%5
  s.suppliers={{kind='base',plot=10+i,city=s.city,ready=n%6,worked=n%2==0}}
 end
 local w=world({a,b});w.maxEvaluations=n%7==0 and 2+n%40 or 512
 if n%3==0 then w.objective=function(r)return math.floor(r.valueQ8/1000)*1000 end end
 M.JointForecast(w,price)
end
'''
original_vm=tests.JointEconomy.vm
def run(path):
    tests.MODEL=path;vms=[]
    def vm(self):
        value=original_vm(self);value.execute(capture);vms.append(value);return value
    tests.JointEconomy.vm=vm
    result=unittest.TestResult();start=time.perf_counter()
    unittest.defaultTestLoader.loadTestsFromTestCase(tests.JointEconomy).run(result)
    extra=vm(tests.JointEconomy());extra.execute(stress)
    elapsed=time.perf_counter()-start
    if result.errors or result.failures:raise AssertionError(str(result.errors+result.failures))
    quotes=[row for value in vms for row in value.globals().__captured.values()]
    calls=sum(value.globals().__priceCalls for value in vms)
    return dict(tests=result.testsRun,worlds=len(quotes),sha256=hashlib.sha256('\n'.join(quotes).encode()).hexdigest(),price_calls=calls,seconds=elapsed),quotes
baseline,qa=run(ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua')
candidate,qb=run(prototype)
assert qa==qb,'Joint results, streams, readiness, plans, values or failures differ'
sys.path.insert(0,str(ROOT/'project/tools/transactions'))
import test_joint_route_economy as routes
route_vm=routes.JointRoutes.vm
def run_routes(path):
    vms=[]
    def vm(self):
        value=route_vm(self)
        value.execute(path.read_text(encoding='utf-8')+'\nM=CSC_AI_EconomyModel')
        value.execute(capture);vms.append(value);return value
    routes.JointRoutes.vm=vm
    result=unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(routes.JointRoutes).run(result)
    if result.errors or result.failures:raise AssertionError(str(result.errors+result.failures))
    quotes=[row for value in vms for row in value.globals().__captured.values()]
    return dict(tests=result.testsRun,worlds=len(quotes),sha256=hashlib.sha256('\n'.join(quotes).encode()).hexdigest()),quotes
ra,qra=run_routes(ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua')
rb,qrb=run_routes(prototype)
assert qra==qrb,'Joint route results or failure behavior differ'
report=dict(scope='Offline prototype only; no live timing claim',baseline=baseline,prototype=candidate,route_baseline=ra,route_prototype=rb,exact_world_results_equal=True,
            source_model_sha256=hashlib.sha256(source.encode()).hexdigest(),
            prototype_model_sha256=hashlib.sha256(prototype.read_bytes()).hexdigest())
(scratch/'joint-starting-reuse-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
