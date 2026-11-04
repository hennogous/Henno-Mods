"""Build the CSC Lua-only v2 policy package, depending on the isolated CE fork.

This builder neither installs files nor carries a native binary. The CE fork
package is built separately, so the distribution boundary is explicit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MOD_ID='d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a07'
CE_FORK_ID='d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a06'
CSC_ID='c5e66bd1-d804-443b-ac3d-1917a20dba3c'
GS_ID='4873eb62-8ccc-4574-b784-dda455e74e68'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(text.encode('utf-8'))

def build(output:Path,*,ce_fork_id:str=CE_FORK_ID)->dict:
    output=output.resolve()
    if output==HERE or output.is_relative_to(HERE):raise ValueError('Output must be outside source directory')
    package=output/'package'
    if package.exists():raise ValueError('Fresh package output required')
    scanner=ROOT/'project/tools/ai_site_planner/adjacency_policy/scan.lua'
    core=ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua'
    sources={
        'Lua/CSC_AI_AdjacencyPolicy.lua':HERE/'policy.lua',
        'Lua/CSC_AI_AdjacencyScan.lua':scanner,
        'Lua/CSC_AI_DistrictBridge.lua':HERE.parent/'ce_frontend/CSC_AI_DistrictBridge.lua',
        'Lua/CSC_CE_Policy.lua':HERE/'gameplay.lua',
    }
    for destination,source in sources.items():
        target=package/destination;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(source.read_bytes())
    # The dependency already exports this core through ImportFiles. Including
    # that VFS name instantiates a read-only cache in the new script context.
    mod=ET.Element('Mod',id=MOD_ID,version='1')
    props=ET.SubElement(mod,'Properties')
    for key,value in dict(Name='CSC CE district policy parity (developer)',
        Description='Unchanged v2 adjacency promotions and weak-site penalties through the CE fork; Lua only. Online, original AI only, stops at turn100.',
        Authors='Henno',CompatibleVersions='2.0',AffectsSavedGames='1').items():
        ET.SubElement(props,key).text=value
    deps=ET.SubElement(mod,'Dependencies')
    for guid,title in [(ce_fork_id,'CE district-score fork (developer)'),(CSC_ID,'Civ Supply Chains'),(GS_ID,'Expansion: Gathering Storm')]:
        ET.SubElement(deps,'Mod',id=guid,title=title)
    actions=ET.SubElement(mod,'InGameActions')
    imports=ET.SubElement(actions,'ImportFiles',id='CSC_CE_Policy_Imports')
    for name in sources:
        if name!='Lua/CSC_CE_Policy.lua':ET.SubElement(imports,'File').text=name
    script=ET.SubElement(actions,'AddGameplayScripts',id='CSC_CE_Policy')
    ET.SubElement(ET.SubElement(script,'Properties'),'LoadOrder').text='999991'
    ET.SubElement(script,'File').text='Lua/CSC_CE_Policy.lua'
    files=ET.SubElement(mod,'Files')
    for name in sources:ET.SubElement(files,'File').text=name
    ET.indent(mod,space='  ')
    write(package/'CSC_CE_Policy.modinfo','<?xml version="1.0" encoding="utf-8"?>\n'+ET.tostring(mod,encoding='unicode')+'\n')
    pins=[dict(path=str(p),sha256=sha(p))for p in [Path(__file__).resolve(),*sources.values(),core]]
    manifest=dict(schema='csc-ce-policy-package-v1',mod_id=MOD_ID,ce_dependency=ce_fork_id,
        built_at=dt.datetime.now(dt.timezone.utc).isoformat(),source_pins=pins,
        scanner_source=str(scanner),scanner_sha256=sha(scanner),
        adjacency_core_from_dependency=dict(vfs='CSC_AdjacencyCore',source=str(core),sha256=sha(core)),
        files=[dict(path=p.relative_to(package).as_posix(),sha256=sha(p))for p in sorted(package.rglob('*'))if p.is_file()],
        guarantees=dict(no_native_binary=True,no_python_runtime=True,no_frida_runtime=True,no_game_control=True),
        status=dict(installed=False,game_run=False,policy='csc-adjacency-policy-v2',native_qualification=False))
    write(output/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    return dict(package=str(package),manifest=str(output/'manifest.json'),context='CSC_CE_Policy')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ce-fork-id',default=CE_FORK_ID)
    a=p.parse_args();print(json.dumps(build(a.output,ce_fork_id=a.ce_fork_id),indent=2))
