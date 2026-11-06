"""Compare the exact two Windows Steam XP2 DLLs without loading either one."""

import argparse
import hashlib
import json
from pathlib import Path
import struct


BASELINE_SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
HOTFIX_SHA = '092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f'
HOTFIX_TIMESTAMP = 1793649108
XP2_IMAGE_SIZE = 12976128

ENTRIES = {
    'RegisterScriptData': 0x5BDAC0,
    'DistrictNetValue': 0x52A440,
    'CalculateDistrictValues': 0x3DFEE0,
    'GetBestDistrict': 0x3E4A50,
    'DistrictPresentValueOf': 0x3E7F40,
}
CALLS = {
    'DoTurnActivate to CalculateDistrictValues': (0x3E293C, 'CalculateDistrictValues'),
    'PlotAnalysis to DistrictNetValue': (0x3E30B9, 'DistrictNetValue'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Image:
    def __init__(self, path, expected_sha):
        self.data = path.read_bytes()
        self.sha256 = hashlib.sha256(self.data).hexdigest()
        require(self.sha256 == expected_sha, f'Unexpected artifact identity: {path}')
        pe, = struct.unpack_from('<I', self.data, 0x3C)
        require(self.data[pe:pe + 4] == b'PE\0\0', 'Expected PE header')
        machine, count, self.timestamp, _, _, optional_size, _ = struct.unpack_from('<HHIIIHH', self.data, pe + 4)
        optional = pe + 24
        require(machine == 0x8664 and self.data[optional:optional + 2] == b'\x0b\x02', 'Expected AMD64 PE32+')
        self.image_size, = struct.unpack_from('<I', self.data, optional + 56)
        self.directories = [struct.unpack_from('<II', self.data, optional + 112 + 8 * i) for i in range(16)]
        self.sections = {}
        for i in range(count):
            name, size, rva, raw_size, offset = struct.unpack_from('<8sIIII', self.data, optional + optional_size + 40 * i)
            self.sections[name.rstrip(b'\0').decode('ascii')] = (rva, size, offset, raw_size)

    def section(self, name):
        _, _, offset, size = self.sections[name]
        return self.data[offset:offset + size]

    def at(self, rva, size):
        for start, _, offset, length in self.sections.values():
            if start <= rva and rva + size <= start + length:
                pos = offset + rva - start
                return self.data[pos:pos + size]
        raise ValueError(f'Unmapped file range at {rva:#x}')

    def identity(self):
        return dict(sha256=self.sha256, timestamp=self.timestamp, image_size=self.image_size,
                    file_size=len(self.data), certificate_size=self.directories[4][1])


def normalize_build_metadata(image, build_id):
    """Remove the inspected build-path token, stamps and CodeView PDB identity."""
    content = bytearray(image.section('.rdata'))
    start = image.sections['.rdata'][0]

    def clear(rva, size):
        offset = rva - start
        require(0 <= offset <= len(content) - size, 'Metadata outside .rdata')
        content[offset:offset + size] = b'\0' * size

    export_rva, _ = image.directories[0]
    clear(export_rva + 4, 4)  # IMAGE_EXPORT_DIRECTORY.TimeDateStamp
    debug_rva, debug_size = image.directories[6]
    require(debug_size % 28 == 0, 'Misaligned IMAGE_DEBUG_DIRECTORY')
    for rva in range(debug_rva, debug_rva + debug_size, 28):
        clear(rva + 4, 4)  # IMAGE_DEBUG_DIRECTORY.TimeDateStamp
        debug_type, _, data_rva = struct.unpack('<III', image.at(rva + 12, 12))
        if debug_type == 2:
            require(image.at(data_rva, 4) == b'RSDS', 'Expected CodeView PDB record')
            clear(data_rva + 4, 16)  # PDB GUID. Keep the age and the rest of the path.
    count = 0
    for separator in (b'\\', b'/'):
        path_component = separator.join((b'work', build_id, b''))
        count += content.count(path_component)
        content = content.replace(path_component, separator.join((b'work', b'0000000000000000', b'')))
    return content, count


def audit(before, after):
    require(before.sections == after.sections, 'Section layouts differ')
    require(before.image_size == after.image_size == XP2_IMAGE_SIZE and after.timestamp == HOTFIX_TIMESTAMP,
            'Unexpected image size or timestamp')
    require(all(a == b for i, (a, b) in enumerate(zip(before.directories, after.directories)) if i != 4),
            'A mapped PE directory changed location or size')
    sections = {name: before.section(name) == after.section(name) for name in before.sections}
    require(all(equal for name, equal in sections.items() if name != '.rdata'), 'Unexpected mapped section difference')
    old_data, old_paths = normalize_build_metadata(before, b'26d31e7d2eca7bbe')
    new_data, new_paths = normalize_build_metadata(after, b'e9c5035e29e72a4c')
    require(old_data == new_data and old_paths == new_paths == 533, 'Unexplained .rdata difference')

    entries = {name: dict(rva=hex(rva), prefix=after.at(rva, 32).hex()) for name, rva in ENTRIES.items()}
    callers = {}
    for name, (rva, target) in CALLS.items():
        instruction = after.at(rva, 5)
        return_rva = rva + len(instruction)
        require(instruction[0] == 0xE8 and return_rva + struct.unpack_from('<i', instruction, 1)[0] == ENTRIES[target],
                f'Unexpected direct call: {name}')
        callers[name] = dict(call_rva=hex(rva), return_rva=hex(return_rva), bytes=instruction.hex(), target=target)

    return dict(baseline=before.identity(), hotfix=after.identity(), sections_equal=sections,
                text_bytes=len(after.section('.text')), build_paths=new_paths, normalized_rdata_equal=True,
                entries=entries, callers=callers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('hotfix', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(Image(args.baseline, BASELINE_SHA), Image(args.hotfix, HOTFIX_SHA)), indent=2))
