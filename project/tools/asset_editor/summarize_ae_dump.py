"""Preserve dump metadata and raw module-relative stack candidates before cleanup.

This is a file-only summary, not a symbolic backtrace or a replacement for heap
memory. Assertion snapshots without an exception stream are supported.
"""
import json
import mmap
from pathlib import Path
import struct
import sys


def summarize(path):
    with Path(path).open('rb') as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as data:
        def read(fmt, offset):
            return struct.unpack_from('<' + fmt, data, offset)

        if data[:4] != b'MDMP':
            raise ValueError('Not a Windows dump')
        count, directory = read('II', 8)
        streams = {read('III', directory + i * 12)[0]: read('III', directory + i * 12)[1:]
                   for i in range(count)}
        if not {3, 4, 7}.issubset(streams):
            raise ValueError('Required thread/module/system streams missing')
        if read('H', streams[7][1])[0] != 9:
            raise ValueError('Only x64 stack summaries are supported')
        result = {'source': str(path), 'bytes': len(data), 'streams': sorted(streams),
                  'dump_flags': hex(read('Q', 24)[0]),
                  'limitation': 'Raw stack candidates, not an unwound or symbolic backtrace. Heap memory is not preserved.',
                  'modules': [], 'threads': []}
        modules = []
        offset = streams[4][1]
        for i in range(read('I', offset)[0]):
            base, size, checksum, timestamp, name_offset = read('QIIII', offset + 4 + i * 108)
            length = read('I', name_offset)[0]
            name = data[name_offset + 4:name_offset + 4 + length].decode('utf-16le')
            modules.append((base, size, name))
            result['modules'].append({'name': name, 'base': hex(base), 'bytes': size, 'timestamp': timestamp})
        if 6 in streams:
            offset = streams[6][1]
            code, flags, nested, address = read('IIQQ', offset + 8)
            result['exception'] = {'thread': read('I', offset)[0], 'code': hex(code), 'address': hex(address)}
        offset = streams[3][1]
        for i in range(read('I', offset)[0]):
            row = offset + 4 + i * 48
            thread_id = read('I', row)[0]
            start, size, rva = read('QII', row + 24)
            candidates = []
            for j in range(min(size, 65536) // 8):
                value = read('Q', rva + j * 8)[0]
                for base, module_size, name in modules:
                    if base <= value < base + module_size:
                        candidates.append({'stack_offset': j * 8, 'module': name, 'module_offset': hex(value - base)})
                        break
            result['threads'].append({'id': thread_id, 'stack_start': hex(start), 'stack_bytes': size,
                                      'candidates': candidates})
        return result


if __name__ == '__main__':
    print(json.dumps(summarize(sys.argv[1]), indent=2))
