"""Read-only evidence for Religion's desaturation and overlay-pass migration.

Requires pefile and capstone supplied via --dependencies. Reads only a shipped
executable; never attaches to or runs Civ. Exact ranges are for the pinned DX11
build, not function-boundary claims from an automatic disassembler.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


EXE_SHA256 = 'e7450823cc8e00468cff7b9d7b97c63140eae38ae1d774ba4efa437556c42d63'
RANGES = {
    'lua_desaturation_binding': (0x14019BAC0, 0x53),
    'desaturation_queue_write': (0x1401994A0, 0x44),
    'desaturation_command_type': (0x1401962E0, 0x64),
    'desaturation_render_handler_registration': (0x14054BFC2, 0x2B),
    'desaturation_target_write': (0x140545D80, 0x0D),
    'desaturation_interpolation': (0x140556B70, 0x64),
    'overlay_zero_comparison_value': (0x14054D68A, 0x04),
    'overlay_mask_selection': (0x14054EFD3, 0x29),
    'primary_overlay_render_call': (0x14054F022, 0x1A),
    'overlay_render_mask_argument': (0x14021BBC0, 0x38),
    'artdef_pass_read': (0x14021AA62, 0x19),
    'artdef_pass_to_bitmask': (0x14021AC14, 0x18),
    'overlay_pass_mask_filter': (0x14021C010, 0x2B),
    'pressure_clock_update': (0x14022C380, 0x53),
    'pressure_clock_sample': (0x14022A7D0, 0x16),
    'pressure_uv_phase': (0x14022AA55, 0x22),
    'pressure_reset_counts': (0x14022B7D0, 0x36),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.dependencies:
        sys.path.insert(0, str(args.dependencies))
    import pefile
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64

    data = args.executable.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXE_SHA256:
        raise ValueError('Executable differs from the inspected build; re-establish ranges first')
    pe = pefile.PE(data=data)
    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    observations = {}
    for name, (address, size) in RANGES.items():
        raw = pe.get_data(address - base, size)
        instructions = list(decoder.disasm_lite(raw, address))
        assert sum(row[1] for row in instructions) == size, name
        observations[name] = {
            'address': hex(address), 'size': size, 'bytes': raw.hex(),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'instructions': [f'{a:#x}: {mnemonic} {operand}'.rstrip()
                             for a, _, mnemonic, operand in instructions],
        }

    def contains(name, fragment):
        assert any(fragment in line for line in observations[name]['instructions']), (name, fragment)

    contains('desaturation_command_type', '[rax + 4], 0x2b')
    contains('desaturation_target_write', 'movss dword ptr [rip + 0x1de47a0], xmm0')
    contains('desaturation_interpolation', 'minss xmm2, xmm0')
    rate = struct.unpack('<f', pe.get_data(0x140FA4048 - base, 4))[0]
    assert rate == 2.0
    contains('overlay_mask_selection', 'mov ebx, 3')
    contains('overlay_zero_comparison_value', 'xorps xmm13, xmm13')
    contains('overlay_mask_selection', 'cmova ebx, eax')
    contains('primary_overlay_render_call', 'mov r9d, ebx')
    contains('primary_overlay_render_call', 'call 0x14021bbc0')
    contains('overlay_render_mask_argument', 'mov r14d, r9d')
    contains('artdef_pass_to_bitmask', 'shl eax, cl')
    contains('overlay_pass_mask_filter', 'test dword ptr [rbx], r14d')
    contains('pressure_clock_update', 'addss xmm0, dword ptr [rax + 0x144]')
    contains('pressure_reset_counts', 'mov dword ptr [rax + 0x158], ecx')
    contains('pressure_reset_counts', 'mov dword ptr [rax + 0x170], ecx')
    # Pass 0 stays in the primary stage on both sides of desaturation zero;
    # Pass 1 is excluded while positive, then included at zero.
    masks = {'positive_desaturation': 1, 'zero_desaturation': 3}
    assert all(mask & (1 << 0) for mask in masks.values())
    assert not (masks['positive_desaturation'] & (1 << 1))
    assert masks['zero_desaturation'] & (1 << 1)
    evidence = {
        'executable': str(args.executable), 'sha256': digest,
        'method': 'Offline PE bytes and Capstone disassembly; no process interaction',
        'observations': observations,
        'desaturation_target': '0x14232a52c', 'desaturation_current': '0x14232a528',
        'interpolation_units_per_second': rate, 'full_one_to_zero_seconds': 1 / rate,
        'primary_stage_masks': masks,
        'pass_encoding': '1 << ArtDef Pass',
        'pressure_phase': 'Each layer has its own accumulated clock at +0x144',
        'pressure_reset': 'ResetAllWaves clears that layer\'s record counts, not a shared clock',
        'fix': 'CSC flows Pass 0 / priority 20; immediate activation; no transition timer',
        'limits': 'Explains a render-stage discontinuity; native visual acceptance remains unobserved',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print('Verified Religion half-second interpolation, Pass 1 migration, stable Pass 0 and per-layer clocks:', args.output)


if __name__ == '__main__':
    main()
