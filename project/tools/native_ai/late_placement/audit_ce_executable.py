"""Verify CE's recovered Steam DX11 address pairs from the exact PE files."""

import argparse
import json
from pathlib import Path
import struct

from audit_xp2_hotfix import Image, require


REFERENCE_SHA = 'e7450823cc8e00468cff7b9d7b97c63140eae38ae1d774ba4efa437556c42d63'
HOTFIX_SHA = 'd1a0cfd439e7451be515f47595cfa0b6b983f56d1faf4ea434a4ce3b21491ebe'

# Start RVAs and the first unwind range length. Mask only the identified
# RIP-relative operands and near call/jump displacements in that range.
ENTRIES = {
    'PublishEvents': (0x6E260, 0x6D500, 164,
                      (0xA, 0x11, 0x25, 0x2A, 0x32, 0x39, 0x43, 0x4D,
                       0x54, 0x6D, 0x74, 0x7B, 0x84, 0x89, 0x93)),
    'ForgeUI::GetLock': (0x88B330, 0x88B9B0, 44, (0x11, 0x1C)),
    'ForgeUI::ReleaseLock': (0x8948A0, 0x895000, 64, (0xA, 0x36)),
}

# Each pair names the same instruction and at least the next ten bytes.
# Keep more than one independent reference for each mutable global.
GLOBALS = {
    'Lua critical section': (0x3552FA0, 0x3553FA0, ((0x4D5374, 0x4D48D4), (0xDB3738, 0xDB3A68))),
    'ForgeUI manager slot': (0x235F7C8, 0x23607C8, ((0x3B9DC, 0x3ADEC), (0x16AEA4, 0x16A5E4))),
}


def unwind_ranges(image):
    address, size = image.directories[3]
    return {start: end for start, end, _ in struct.iter_unpack('<III', image.at(address, size))}


def mask_rel32(data, displacements):
    masked = bytearray(data)
    for pos in displacements:
        masked[pos:pos + 4] = bytes(4)
    return masked


def audit(reference, hotfix):
    old = Image(reference, REFERENCE_SHA)
    new = Image(hotfix, HOTFIX_SHA)
    old_ranges, new_ranges = unwind_ranges(old), unwind_ranges(new)
    entries = {}
    for role, (previous, current, length, masks) in ENTRIES.items():
        require(old_ranges[previous] - previous == new_ranges[current] - current == length,
                f'Unexpected unwind extent for {role}')
        before, after = old.at(previous, length), new.at(current, length)
        require(mask_rel32(before, masks) == mask_rel32(after, masks), f'Changed code for {role}')
        entries[role] = dict(reference=hex(previous), hotfix=hex(current),
                             compared_bytes=length, hotfix_prefix=after[:24].hex())

    globals_ = {}
    for role, (previous, current, anchors) in GLOBALS.items():
        for old_at, new_at in anchors:
            before, after = old.at(old_at, 17), new.at(new_at, 17)
            require(mask_rel32(before, (3,)) == mask_rel32(after, (3,)), f'Changed reference to {role}')
            for code, rva, target in ((before, old_at, previous), (after, new_at, current)):
                displacement, = struct.unpack_from('<i', code, 3)
                require(rva + 7 + displacement == target, f'Unexpected reference target for {role}')
        globals_[role] = dict(reference=hex(previous), hotfix=hex(current),
                              references=[[hex(a), hex(b)] for a, b in anchors])
    return dict(reference=old.identity(), hotfix=new.identity(), entries=entries, globals=globals_)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('hotfix', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.reference, args.hotfix), indent=2))
