"""Stage the isolated CSC dev CE port for Steam build 26595377."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct

from audit_ce_executable import ENTRIES, GLOBALS, REFERENCE_SHA, mask_rel32, unwind_ranges
from audit_ce_gamecore_relocation import audit
from audit_xp2_hotfix import BASELINE_SHA, Image, require
from ce_replay import STEAM_26595377_CORE_SHA as GAMECORE_SHA, STEAM_26595377_EXE_SHA as EXE_SHA


GAMECORE_TIMESTAMP = 1794358453
PROJECT = 'CivilizationVI_CommunityExtension'
SHARED = {'PublishEvents': 0x6D630, 'ForgeUI::GetLock': 0x88BA40, 'ForgeUI::ReleaseLock': 0x894F00}
REFERENCES = {'Lua critical section': (0x4D5834, 0xDB3AB8), 'ForgeUI manager slot': (0x3B39C, 0x16AF54)}

# The repeated names in the code have identical instruction templates. These
# choices use their Lua class/method string references, or a resolved native
# caller for CopyTreeAnalysis. National Parks has the same 22-byte unwind body.
REVIEWED_CODE = {
    0x1B2E0: 0x1B2E0, 0x1EFF0: 0x1EFF0, 0x24DA0: 0x24DA0,
    0x99F60: 0x99F60, 0xD6160: 0xD6160, 0x6D86E0: 0x6D8720,
    0x6ECBD0: 0x6ECC10, 0x6EE9B0: 0x6EE9F0, 0x6EEB10: 0x6EEB50,
    0x6F34F0: 0x6F3530, 0x6F3650: 0x6F3690, 0x7139C0: 0x713A00,
}
# Checked by resolving RIP-relative references inside matched code.
REVIEWED_DATA = {
    0x9B7680: 0x9B7680, 0x9FA930: 0x9FA910, 0xB66CB0: 0xB66CB0,
    0xB8AA60: 0xB8AA60, 0xB8AA68: 0xB8AA68, 0xB8F648: 0xB8F648,
}
FINGERPRINTS = {
    'fingerprint_register': 'RegisterScriptDataRva', 'fingerprint_net': 'DistrictNetValueRva',
    'fingerprint_cache': 'CalculateDistrictValuesRva', 'fingerprint_best': 'GetBestDistrictRva',
    'fingerprint_present': 'DistrictPresentValueRva', 'fingerprint_location': 'DistrictLocationRva',
    'fingerprint_request_update': 'RequestUpdateRva', 'fingerprint_request_assignment': 'AssignRequestValueRva',
    'fingerprint_district_type_count': 'CountDistrictTypeRva', 'fingerprint_district_at': 'DistrictAtRva',
    'ImprovementNetPrefix': 'ImprovementNetValueRva', 'BuildingNetPrefix': 'BuildingNetValueRva',
    'BuildingNominationRestoreFlag': 'BuildingNominationRestoreFlagRva',
    'BuildingNominationCompare': 'BuildingNominationComparisonRva',
}


def verify_executable(reference, current):
    ranges = unwind_ranges(current)
    for name, (old, _, length, masks) in ENTRIES.items():
        new = SHARED[name]
        require(ranges.get(new) == new + length and
                mask_rel32(reference.at(old, length), masks) == mask_rel32(current.at(new, length), masks),
                f'Unexpected executable entry for {name}')
    for name, (_, expected, before) in GLOBALS.items():
        for (old, _), new in zip(before, REFERENCES[name], strict=True):
            instructions = current.at(new, 17)
            require(mask_rel32(reference.at(old, 17), (3,)) == mask_rel32(instructions, (3,))
                    and new + 7 + struct.unpack_from('<i', instructions, 3)[0] == expected,
                    f'Unexpected executable global for {name}')


def decode_bytes(source):
    return bytes(int(byte, 16) for byte in re.findall(r'(?:0x|\\x)([0-9a-fA-F]{2})\b', source))


def format_bytes(data, escaped=False):
    if escaped:
        return ''.join(f'\\x{byte:02x}' for byte in data)
    return ', '.join(f'0x{byte:02x}' for byte in data)


def stage(source, output, reference_core, reference_exe, gamecore, executable):
    old_core = Image(reference_core, BASELINE_SHA)
    new_core = Image(gamecore, GAMECORE_SHA)
    new_exe = Image(executable, EXE_SHA)
    require(new_core.timestamp == GAMECORE_TIMESTAMP, 'Unexpected GameCore timestamp')
    verify_executable(Image(reference_exe, REFERENCE_SHA), new_exe)
    located = audit(source / PROJECT, reference_core, gamecore)
    by_file = defaultdict(dict)
    named = {}
    for row in located['targets']:
        name, old, candidates = row['name'], int(row['old'], 16), row['candidates']
        if candidates is None:
            new = REVIEWED_DATA[old]
        elif len(candidates) == 1 and candidates[0][2] >= 15:
            new = candidates[0][0]
        else:
            new = REVIEWED_CODE[old]
            require(new in {c[0] for c in candidates}, f'Invalid reviewed candidate for {name}')
        row['selected'] = hex(new)
        by_file[row['file']][name, old] = new
        named[name] = (old, new)

    def verify_call(call, callee, return_address=False):
        offsets = named[call]
        for image, address, target in zip((old_core, new_core), offsets, named[callee], strict=True):
            address -= 5 if return_address else 0
            code = image.at(address, 5)
            require(code[0] == 0xE8 and address + 5 + struct.unpack_from('<i', code, 1)[0] == target,
                    f'Unexpected call target at {call}')

    verify_call('DistrictAggregationCallRva', 'CalculateDistrictValuesRva')
    verify_call('NetValueFromPlotAnalysisReturnRva', 'DistrictNetValueRva', True)
    verify_call('ImprovementRowCallRva', 'ImprovementNetValueRva')
    verify_call('WonderRowCallRva', 'BuildingNetValueRva')
    verify_call('OrdinaryBuildingForecastCallRva', 'BuildingNetValueRva')
    verify_call('OrdinaryBuildingNominationCallRva', 'GetBestBuildingRva')
    verify_call('BuildFromCityUnitReturnRva', 'InitializeUnitRequestRva', True)
    verify_call('ManagerUpdateReturnRva', 'TreeUpdateRva', True)

    def translated_guard(body, name, adjustment=0, escaped=False):
        old, new = named[name]
        recorded = decode_bytes(body)
        require(recorded and old_core.at(old + adjustment, len(recorded)) == recorded,
                f'Prior prefix mismatch for {name}')
        actual = new_core.at(new + adjustment, len(recorded))
        return body if actual == recorded else format_bytes(actual, escaped)

    # Source and output remain separate. The reviewed previous release stays
    # usable, while this copy has one exact executable and GameCore profile.
    shutil.copytree(source, output)
    root = output / PROJECT
    for relative, addresses in by_file.items():
        path = root / relative
        data = path.read_text(encoding='utf-8')
        for (name, before), after in addresses.items():
            if before != after:
                data, count = re.subn(rf'(\b{re.escape(name)}\s*=\s*)0x0*{before:x}\b',
                                      lambda m: f'{m[1]}{after:#x}', data, flags=re.I)
                require(count == 1, f'Expected one source declaration for {relative}:{name}')
        path.write_text(data, encoding='utf-8')

    guards = ('AIDistrictScores.cpp', 'native/target_identity.h', 'native/builder_protection.inl',
              'native/district_repair_admission.inl', 'native/economy_pricing.inl',
              'native/native_site_pricing.inl', 'native/purchase_ownership_completion.inl',
              'native/material_development.inl', 'native/material_worker_dispatch.inl')
    for relative in guards:
        path = root / relative
        data = path.read_text(encoding='utf-8')
        data = re.sub(r'(\b(\w+)\[\d*\]\s*=\s*\{)([\s0-9a-fx,]+)(\})',
                      lambda m: m[1] + translated_guard(m[3], FINGERPRINTS[m[2]]) + m[4]
                      if m[2] in FINGERPRINTS else m[0], data)
        data = re.sub(r'(\{(?:[\w]+::)?(\w+Rva),\s*\{)([\s0-9a-fx,]+)(\}\})',
                      lambda m: m[1] + translated_guard(m[3], m[2]) + m[4], data)
        data = re.sub(r'(\{(?:[\w]+::)?(\w+Rva),\s*")((?:\\x[0-9a-fA-F]{2})+)(")',
                      lambda m: m[1] + translated_guard(m[3], m[2], escaped=True) + m[4], data)
        data = re.sub(r'(prefix\(base, (\w+Rva)( - 5)?, std::to_array<Byte>\(\{)([^}]+)(\})',
                      lambda m: m[1] + translated_guard(m[4], m[2], -5 if m[3] else 0) + m[5], data)
        data = data.replace('092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f', GAMECORE_SHA)
        data = data.replace('1793649108u', f'{GAMECORE_TIMESTAMP}u')
        data = data.replace('XP2 hotfix 092abfbb', 'XP2 build 26595377').replace('XP2 092abfbb', 'XP2 build 26595377')
        data = data.replace('XP2 Windows Steam November 2026 hotfix (build 26407122). Its .text and\n'
                            '// section layout match the previous image.',
                            'XP2 Windows Steam build 26595377, verified against the prior CE call sites.')
        path.write_text(data, encoding='utf-8')

    path = root / 'Runtime.cpp'
    data = path.read_text(encoding='utf-8')
    profile = f'''// The GameCore offsets in this build are scoped to this exact pair.
			// See the 26595377 relocation report for the unwind and reference checks.
			constexpr ExecutableProfile profiles[] = {{
				{{"Steam DX11 build 26595377",
				 "{EXE_SHA}",
				 "{GAMECORE_SHA}",
				 0x6d630, 0x3553fa0, 0x88ba40, 0x894f00, 0x23607c8,
				 {{{format_bytes(new_exe.at(SHARED['PublishEvents'], 24))}}}}},
			}};'''
    data, count = re.subn(r'// Windows Steam DX11\..+?constexpr ExecutableProfile profiles\[\] = \{.+?\n\s*\};',
                          lambda _: profile, data, flags=re.S)
    require(count == 1, 'Expected one prior executable profile table')
    path.write_text(data, encoding='utf-8')
    located['executable'] = new_exe.identity()
    located['executable_entries'] = SHARED
    located['executable_global_references'] = REFERENCES
    (output / 'native-relocation.json').write_text(json.dumps(located, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'reference-core', 'reference-exe', 'gamecore', 'executable'):
        parser.add_argument('--' + name, type=Path, required=True)
    stage(**vars(parser.parse_args()))
