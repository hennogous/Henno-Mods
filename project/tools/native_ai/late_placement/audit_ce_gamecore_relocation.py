"""Find candidate relocations for the declared CE gameplay addresses.

Only CE's declared code targets are inspected. A candidate is found from
literal instruction runs, masking x64 PC-relative operands. Review call
targets, data references, and guards separately before enabling hooks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_GRP_CALL, CS_GRP_JUMP
from capstone.x86 import X86_OP_MEM, X86_OP_IMM, X86_REG_RIP

from audit_xp2_hotfix import Image


def targets(source):
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if (path.suffix not in ('.h', '.cpp', '.inl') or {'include', 'tests'}.intersection(relative.parts)
                or path.name == 'Runtime.cpp'):
            continue
        for match in re.finditer(r'\b(\w+(?:Rva|OFFSET)|CHANGE_NEUTRALIZED_TURNS)\s*=\s*0x([0-9a-fA-F]{3,8})\b',
                                 path.read_text(encoding='utf-8', errors='replace')):
            yield str(relative), match[1], int(match[2], 16)


def pattern(instructions):
    result = []
    fixed = 0
    for insn in instructions:
        data = bytes(insn.bytes)
        start = size = 0
        if any(op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP for op in insn.operands):
            start, size = insn.disp_offset, insn.disp_size
        elif ((insn.group(CS_GRP_JUMP) or insn.group(CS_GRP_CALL))
              and any(op.type == X86_OP_IMM for op in insn.operands)):
            start, size = insn.imm_offset, insn.imm_size
        if size:
            result.extend((re.escape(data[:start]), b'.' * size, re.escape(data[start + size:])))
        else:
            result.append(re.escape(data))
        fixed += len(data) - size
    return b''.join(result), fixed


def find(disassembler, old, new_text, new_start, address):
    # The relative-operand mask tolerates relocation and reordered callees.
    # Record independent fixed bytes and the total span of the matching
    # instructions. Small thunks need a caller or data-reference review.
    instructions = list(disassembler.disasm(old.at(address, 512), address))
    if not instructions:
        return []
    left = max(0, address - new_start - 0x14000)
    right = min(len(new_text), address - new_start + 0x14000)
    sample = new_text[left:right]
    for count in (90, 55, 36, 22, 14, 9, 6, 4, 2):
        prefix = instructions[:count]
        regex, fixed = pattern(prefix)
        if fixed < 6:
            continue
        matches = [left + new_start + match.start() for match in re.finditer(b'(?=' + regex + b')', sample, re.S)]
        if matches:
            length = prefix[-1].address + prefix[-1].size - address
            return [(candidate, length, fixed) for candidate in matches]
    return []


def audit(source, reference, update):
    # The caller records exact full-file hashes; candidates are not installation
    # authority until checked against the supported build and runtime tests.
    old, new = (Image(path, hashlib.sha256(path.read_bytes()).hexdigest()) for path in (reference, update))
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True
    begin, size, *_ = old.sections['.text']
    new_begin = new.sections['.text'][0]
    new_text = new.section('.text')
    matches = {}
    for file, name, address in targets(source):
        if address not in matches:
            matches[address] = (find(decoder, old, new_text, new_begin, address)
                                if begin <= address < begin + size else None)
    rows = [{'file': file, 'name': name, 'old': hex(address), 'candidates': matches[address]}
            for file, name, address in targets(source)]
    return {'reference': old.identity(), 'update': new.identity(), 'targets': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('source', 'reference', 'update'):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(**vars(args)), indent=2))
