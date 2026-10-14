"""Inspect the verified AE 1.1 texture-encoder null-call crash in a local dump.

This is specific to Civ6ToolHost_Win64_DX11_Release.dll's call at RVA 0x4ffc7f.
It reads files only. Full process memory is needed to recover the texture name.
"""
import bisect
import mmap
import struct
import sys
from pathlib import Path


def main(path):
    with Path(path).open('rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        def unpack(fmt, offset):
            return struct.unpack_from('<' + fmt, data, offset)

        count, directory = unpack('II', 8)
        streams = {unpack('III', directory + i * 12)[0]:
                   unpack('III', directory + i * 12)[1:] for i in range(count)}
        ranges = []
        if 5 in streams:
            offset = streams[5][1]
            ranges.extend(unpack('QII', offset + 4 + i * 16)
                          for i in range(unpack('I', offset)[0]))
        if 9 in streams:
            offset = streams[9][1]
            count, cursor = unpack('QQ', offset)
            for i in range(count):
                address, size = unpack('QQ', offset + 16 + i * 16)
                ranges.append((address, size, cursor))
                cursor += size
        ranges.sort()
        starts = [r[0] for r in ranges]

        def read(address, size):
            index = bisect.bisect_right(starts, address) - 1
            if index < 0:
                return b''
            begin, length, offset = ranges[index]
            if address + size > begin + length:
                return b''
            offset += address - begin
            return data[offset:offset + size]

        def pointer(address):
            raw = read(address, 8)
            return struct.unpack('<Q', raw)[0] if raw else 0

        exception = streams[6][1]
        _, context = unpack('II', exception + 160)
        registers = {name: unpack('Q', context + offset)[0] for name, offset in
                     [('rcx', 128), ('rdx', 136), ('rbx', 144), ('rsp', 152),
                      ('rdi', 176), ('r13', 224), ('rip', 248)]}
        print('REGISTERS', {k: hex(v) for k, v in registers.items()})
        offset = streams[4][1]
        native = None
        for i in range(unpack('I', offset)[0]):
            base, size, _, _, string = unpack('QIIII', offset + 4 + i * 108)
            name = data[string + 4:string + 4 + unpack('I', string)[0]].decode('utf-16le')
            if name.endswith('Civ6ToolHost_Win64_DX11_Release.dll'):
                native = base
        return_address = pointer(registers['rsp'])
        print('RETURN_RVA', hex(return_address - native) if native else 'module absent')
        if not native or return_address - native != 0x4ffc81 or registers['rip'] != 0:
            raise SystemExit('Different crash: texture object offsets are not applicable.')
        texture = registers['rbx']
        header = read(texture, 64)
        if not header:
            raise SystemExit('Texture heap memory omitted; a full dump is required.')
        print('TEXTURE_HEADER', struct.unpack('<16I', header))
        name_address = pointer(texture - 16 + 0x450)
        raw_name = bytearray()
        for i in range(512):
            char = read(name_address + i, 1)
            if not char or char == b'\0':
                break
            raw_name.extend(char)
        print('TEXTURE_NAME', raw_name.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    main(sys.argv[1])
