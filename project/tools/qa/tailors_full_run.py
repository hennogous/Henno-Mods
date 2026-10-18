"""Report-only native Tailors test matrix, with automatic native popup handling."""
import argparse
from pathlib import Path
import sys
from csc_qa import ROOT, tuner
from smoke import wait_for_state
import tailors_native as cases

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--disposable-game',action='store_true',required=True)
a=p.parse_args()
tuner.PORT=wait_for_state('CSC_AdjacencyGameplay',300,4318)
states=tuner.states();tuner.states=lambda:states
m=cases.Matrix(a.output)
source=(ROOT/'project/tests/qa/placement.lua').read_text()+'\n'+(ROOT/'project/tests/qa/tailors_world.lua').read_text()
m.command('load controlled game helpers',source)
m.command('load controlled UI helpers',source,'PlotInfo')
m.command('create disposable native Tailors world','TQA.Setup()')
m.command('install reference Workshop',f'TQA.Add("QA","{cases.W}")')
for group in ('static_native','material_local','stage3','stage4_baselined','services','trade','multiseller','regional'):
    try:getattr(cases,group)(m)
    except Exception as exc:
        (a.output/(group+'-blocked.txt')).write_text(str(exc));print('BLOCKED '+group+': '+str(exc),flush=True)
print('Native matrix finished; inspect final assertions and coverage before reporting.',flush=True)
