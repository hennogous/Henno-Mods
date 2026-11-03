"""Read-only DX11 evidence for native path opacity versus pressure-wave fading.

Uses Windows' D3DDisassemble on shipped DXBC blobs; never opens the game process
or edits the shader library. Output includes library/blob hashes and disassembly.
"""
import argparse
import ctypes as C
import hashlib
import json
import re
import struct
from pathlib import Path


def disassemble(code):
    fn = C.WinDLL('d3dcompiler_47.dll').D3DDisassemble
    fn.argtypes = [C.c_void_p, C.c_size_t, C.c_uint, C.c_char_p, C.POINTER(C.c_void_p)]
    fn.restype = C.c_long
    buffer, blob = C.create_string_buffer(code), C.c_void_p()
    assert fn(buffer, len(code), 0, None, C.byref(blob)) == 0
    table = C.cast(blob, C.POINTER(C.POINTER(C.c_void_p))).contents
    try:
        pointer = C.WINFUNCTYPE(C.c_void_p, C.c_void_p)(table[3])(blob)
        size = C.WINFUNCTYPE(C.c_size_t, C.c_void_p)(table[4])(blob)
        return C.string_at(pointer, size).decode('utf-8').rstrip('\0')
    finally:
        C.WINFUNCTYPE(C.c_ulong, C.c_void_p)(table[2])(blob)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shader-library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.shader_library.read_bytes()
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = {'library': str(args.shader_library), 'sha256': hashlib.sha256(data).hexdigest(), 'shaders': []}
    for family in ['PressureOverlayDynamics', 'PathOverlayDynamics']:
        seen = set()
        for hit in re.finditer(family.encode(), data):
            offset = data.rfind(b'DXBC', 0, hit.start())
            assert offset >= 0
            size = struct.unpack_from('<I', data, offset + 24)[0]
            assert offset + size <= len(data) and hit.start() < offset + size
            if offset in seen:
                continue
            seen.add(offset)
            code = data[offset:offset+size]
            text = disassemble(code)
            stage = re.search(r'^(?:ps|vs)_\d_\d', text, re.M)[0]
            name = f'{family}-{offset:06x}-{stage}.txt'
            (args.output/name).write_text(text, encoding='utf-8')
            evidence['shaders'].append({'family': family, 'offset': offset, 'size': size, 'stage': stage,
                'sha256': hashlib.sha256(code).hexdigest(), 'disassembly': name})
            if family == 'PressureOverlayDynamics' and stage == 'ps_5_0':
                # t=(distance-offset)/length; x=2*t-1; fade=1-x^4.
                assert 'add r0.y, v2.x, -cb0[2].z' in text
                assert 'div r0.y, r0.y, cb0[3].w' in text
                assert 'mul r0.y, r0.y, r0.y' in text
                assert 'mad r0.y, -r0.y, r0.y, l(1.000000)' in text
                evidence['pressureFade'] = '1 - (2*t - 1)^4; t=(distance-offset)/length'
            if family == 'PathOverlayDynamics' and stage == 'ps_5_0':
                assert 'gTintColor' in text and 'g_fLength' not in text
                evidence['pathFade'] = 'No endpoint envelope; texture RGBA multiplied by per-path gTintColor'
    assert 'pressureFade' in evidence and 'pathFade' in evidence
    (args.output/'evidence.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print('Native pressure fade and path uniform-opacity shaders verified; disassembly saved:', args.output)


if __name__ == '__main__':
    main()
