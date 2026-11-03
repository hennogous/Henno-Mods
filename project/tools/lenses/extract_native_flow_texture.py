"""Recover the unchanged shipped arrow texture missing from the older SDK pantry.

Scoped to the inspected game Overlay.blp hash. The reflected TextureEntry layout
is corroborated by the preceding HexPlace texture matching SDK pixels exactly.
No game/installed package is written. Keep the original eight RGBA mip levels.
"""
import argparse
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NATIVE_HASH = '807a6a384068c6be91c528421b9fc26571dcaf1a0c9bd22c49d6843569e0c2dd'
PIXEL_HASH = '88d68d9eeb71829da550ed1f66ba2f8da49bd99500022735f3ce0fbcbd6cbe5c'


def extract(package):
    data = package.read_bytes()
    assert hashlib.sha256(data).hexdigest() == NATIVE_HASH, 'Different game package; inspect its directory before extracting'
    assert data[:8] == b'CIVBLP\x02\0'
    # Current serialized entries are 104 bytes. Name slot 32 is FormCorpsArrow;
    # preceding slot 31 is HexPlace_ValidFill_Overlay (SDK pixel parity control).
    entry = 38157
    assert struct.unpack_from('<Q', data, entry + 8)[0] == 32
    assert data[39381:39395] == b'FormCorpsArrow'
    offset, size = struct.unpack_from('<QI', data, entry + 32)
    assert struct.unpack_from('<5H2B', data, entry + 88) == (29, 128, 64, 1, 1, 8, 0)
    big_data = struct.unpack_from('<I', data, 16)[0]
    payload = data[big_data + offset:big_data + offset + size]
    assert len(payload) == size == 43692
    assert hashlib.sha256(payload[:128*64*4]).hexdigest() == PIXEL_HASH
    assert sum(max(1,128 >> n)*max(1,64 >> n)*4 for n in range(8)) == len(payload)
    header = [124, 0x21007, 64, 128, 0, 1, 8] + [0x54585246] + [0]*10
    header += [32, 0x41, 0, 32, 0xff, 0xff00, 0xff0000, 0xff000000, 0x401008, 0, 0, 0, 0]
    return b'DDS ' + struct.pack('<31I', *header) + payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'Civ Supply Chains/Textures/CSC_Lens_FlowArrow.dds')
    args = parser.parse_args()
    result = extract(args.game/'Base/Platforms/Windows/BLPs/Overlay.blp')
    args.output.write_bytes(result)
    print(f'Extracted unchanged 128x64 arrow, eight mip levels: {args.output}')


if __name__ == '__main__':
    main()
