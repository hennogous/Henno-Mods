"""Offline only: compare exact joint-search results under two model versions.

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
parser.add_argument('--control-model',type=Path,required=True)
parser.add_argument('--candidate-model',type=Path,default=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua')
args=parser.parse_args()
scratch=args.output_directory.resolve(strict=True)
assert not scratch.is_relative_to(ROOT),'Generated prototypes belong outside the source tree'
spec=importlib.util.spec_from_file_location('joint_tests',ROOT/'project/tools/ai_economy/test_joint_customer_economy.py')
tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
control_model=args.control_model.resolve(strict=True)
candidate_model=args.candidate_model.resolve(strict=True)
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
baseline,qa=run(control_model)
candidate,qb=run(candidate_model)
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
ra,qra=run_routes(control_model)
rb,qrb=run_routes(candidate_model)
assert qra==qrb,'Joint route results or failure behavior differ'
report=dict(scope='Offline comparisons; no live timing claim',baseline=baseline,candidate=candidate,
            route_baseline=ra,route_candidate=rb,exact_world_results_equal=True,
            control_model_sha256=hashlib.sha256(control_model.read_bytes()).hexdigest(),
            candidate_model_sha256=hashlib.sha256(candidate_model.read_bytes()).hexdigest())
(scratch/'joint-reuse-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
