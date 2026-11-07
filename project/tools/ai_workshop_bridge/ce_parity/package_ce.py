"""Assemble an isolated development CE mod; never overwrite installed CE.

The native DLL is supplied by an explicit complete fork build. The installed CE
package supplies only its small configuration/UI files. A distinct development
identity avoids the local/Workshop duplicate-GUID resolver seen in earlier work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
import xml.etree.ElementTree as ET

MOD = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a06'
UPSTREAM = '3351473b-0746-417a-a618-2b66a04d8f3d'
PREFIX = 'GameCore_XP2_CE_AI'
DLL = PREFIX + '_FinalRelease.dll'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(a):
    source, binary, out = a.ce.resolve(), a.dll.resolve(), a.output.resolve()
    mod_id = str(uuid.UUID(getattr(a, 'mod_id', MOD)))
    if mod_id == UPSTREAM:
        raise ValueError('The local CE candidate needs a distinct identity')
    if out.exists() or not binary.is_file():
        raise ValueError('A fresh output directory and explicit fork DLL are required')
    manifests = list(source.glob('*.modinfo'))
    if len(manifests) != 1:
        raise ValueError('Expected one reference CE manifest')
    tree = ET.parse(manifests[0])
    root = tree.getroot()
    if root.get('id') != UPSTREAM:
        raise ValueError('Unexpected reference CE identity')
    root.set('id', mod_id)
    root.set('version', '1')
    root.find('Properties/Name').text = 'CE AI development fork (local test)'
    root.find('Properties/Description').text = (
        'Experimental CE build with the district-score API. Local research only.')
    root.find('Properties/Authors').text = 'WildW; hennogous development fork'
    root.find('Properties/AffectsSavedGames').text = '1'
    expected = {'Data/Config.sql', 'Data/Dummy.sql',
                'UI/CEWatermark.lua', 'UI/CEWatermark.xml',
                'Binaries/Win64/GameCore_XP2_CE_FinalRelease.dll'}
    if {v.text for v in root.findall('Files/File')} != expected:
        raise ValueError('Reference package layout changed; review before copying')
    out.mkdir(parents=True)
    pins = {str(manifests[0]): sha(manifests[0]), str(binary): sha(binary)}
    for relative in sorted(expected):
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.endswith('.dll'):
            target = target.with_name(DLL)
            shutil.copyfile(binary, target)
        else:
            origin = source / relative
            pins[str(origin)] = sha(origin)
            if relative == 'Data/Config.sql':
                text = origin.read_text(encoding='utf-8-sig')
                if text.count(UPSTREAM) != 1 or text.count('GameCore_XP2_CE') != 1:
                    raise ValueError('Reference frontend selector changed')
                target.write_text(text.replace(UPSTREAM, mod_id).replace(
                    'GameCore_XP2_CE', PREFIX), encoding='utf-8')
            else:
                shutil.copyfile(origin, target)
    for node in root.iter('File'):
        if node.text and node.text.endswith('GameCore_XP2_CE_FinalRelease.dll'):
            node.text = 'Binaries/Win64/' + DLL
    ET.indent(tree, space='  ')
    tree.write(out / 'CE_AI_Development.modinfo', encoding='utf-8', xml_declaration=True)
    receipt = dict(mod_id=mod_id, dll=DLL, dll_sha256=sha(binary), input_pins=pins,
                   upstream_installation_modified=False, development_only=True,
                   source_repo='https://github.com/hennogous/CivilizationVI_CommunityExtension')
    (out.parent / (out.name + '-receipt.json')).write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('ce', 'dll', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--mod-id', default=MOD, help='Distinct local CE identity')
    print(json.dumps(build(parser.parse_args()), indent=2))
