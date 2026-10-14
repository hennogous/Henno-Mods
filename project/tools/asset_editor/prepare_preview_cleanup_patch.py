"""Prepare a one-byte, version-locked AE preview cleanup patch. Never installs it."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ORIGINAL_SHA256 = 'b1855d6319f0ce804162342252892247fd3540da25f0f6872d64713f4a38f990'
METHOD_RVA = 0xd7a0


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(source, output):
    data = source.read_bytes()
    if sha(data) != ORIGINAL_SHA256:
        raise ValueError('Unsupported DLL version: no files changed')
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    if data[pe:pe+4] != b'PE\0\0':
        raise ValueError('Missing PE header')
    sections, optional_size = struct.unpack_from('<H', data, pe+6)[0], struct.unpack_from('<H', data, pe+20)[0]
    table = pe + 24 + optional_size
    offsets = []
    for i in range(sections):
        virtual_size, rva, raw_size, raw = struct.unpack_from('<IIII', data, table + i*40 + 8)
        if rva <= METHOD_RVA < rva + min(virtual_size, raw_size):
            offsets.append(raw + METHOD_RVA - rva)
    if len(offsets) != 1:
        raise ValueError('Method RVA does not resolve uniquely')
    body = offsets[0]
    flags = struct.unpack_from('<H', data, body)[0]
    if flags & 3 != 3 or flags >> 12 != 3:
        raise ValueError('Unexpected method header')
    code = body + (flags >> 12)*4
    if struct.unpack_from('<I', data, body+4)[0] != 0x8e:
        raise ValueError('Unexpected method length')
    if data[code+0xf:code+0x14] != bytes.fromhex('2c022b7a04'):
        raise ValueError('Unexpected cleanup branch')
    position = code + 0x12
    patched = bytearray(data)
    patched[position] = 0
    output.mkdir(parents=True, exist_ok=False)
    (output/'Firaxis.AssetPreviewing.original.dll').write_bytes(data)
    (output/'Firaxis.AssetPreviewing.patched.dll').write_bytes(patched)
    manifest = {
        'source': str(source.resolve()), 'assembly': 'Firaxis.AssetPreviewing.dll',
        'method': 'Firaxis.AssetPreviewing.PreviewerDocumentService::DocumentRegistry_DocumentRemoved',
        'method_token': '0x060002b8', 'method_rva': hex(METHOD_RVA),
        'file_offset': hex(position), 'il_offset': '0x12',
        'old_byte': '7a', 'new_byte': '00',
        'old_branch_target': 'IL_008d (return)', 'new_branch_target': 'IL_0013 (preview cleanup)',
        'original_sha256': sha(data), 'patched_sha256': sha(patched),
        'size': len(data), 'changed_bytes': 1,
        'runtime_validation': 'Pending manual AE validation; offline validator must pass before installation',
    }
    (output/'patch-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
