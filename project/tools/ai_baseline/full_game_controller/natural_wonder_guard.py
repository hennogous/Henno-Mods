"""Opt-in, per-controller NaturalWonder presentation guard; no game I/O on install.

The shipped Close handler advances its local popup queue or releases its event
lock. It sends no political response, order, turn activation or gameplay policy.
"""
import hashlib
import json
import re
import time
import types
from pathlib import Path

RESOURCE = Path(__file__).with_name('natural_wonder_playback.lua')
MARKER = 'CSC_NATURAL_WONDER_RELEASE_REQUESTED'
JSON_MARKER = 'CSC_NATURAL_WONDER_GUARD='
MAX_ACKNOWLEDGEMENTS = 8


def eligible(proof, target):
    return (type(target) is int and isinstance(proof, dict)
            and type(proof.get('turn')) is int and type(proof.get('remaining')) is int
            and proof.get('active') is True and proof.get('local_player') == -1
            and proof.get('player0_human') is False and proof.get('player0_alive') is True
            and 1 <= proof['remaining'] <= 5 and target-proof['turn'] == proof['remaining'])


def install(controller):
    """Wrap only this existing instance's release_disaster; never touch its class."""
    if getattr(controller, '_natural_wonder_guard', None) is not None: return controller
    original = controller.release_disaster
    state = dict(version=1, acknowledgements={}, blocked_targets=set(), attempts={}, reads=0)
    controller._natural_wonder_guard = state

    def record(self, name, value):
        self.diagnostics.write(self.root/'natural-wonder-recoveries'/name, value)

    def wrapped(self, target):
        result = original(target)
        state['reads'] += 1
        proof = self.state_read('natural-wonder-core-proof-'+str(target))
        if not eligible(proof, target): return result
        if target in state['blocked_targets'] or state['acknowledgements'].get(target, 0) >= MAX_ACKNOWLEDGEMENTS:
            return result
        self.states()
        if 'NaturalWonderPopup' not in self.state: return result
        # Every candidate has a fresh Core read and UI visibility/stack check.
        # A confirmed no-op may be checked again; an ambiguous transmission may
        # never replay in the same interval. Multiple queued wonders are separate
        # native acknowledgements, each bounded by the eight-ack interval cap.
        attempt = state['attempts'].get(target, 0)+1; state['attempts'][target] = attempt
        name = f'{target}-{attempt:03d}.json'
        code = RESOURCE.read_text(encoding='utf-8')
        for key, value in dict(CORE_TURN=proof['turn'], TARGET_TURN=target, CORE_ACTIVE=proof['active'],
                               REMAINING=proof['remaining'], CORE_LOCAL=proof['local_player'], CORE_HUMAN=proof['player0_human']).items():
            code = code.replace('__'+key+'__', str(value).lower())
        receipt = dict(context='NaturalWonderPopup', source_path='/InGame/WorldPopups/NaturalWonderPopup',
                       target=target, attempt=attempt, core_proof=proof, phase='intent-reserved',
                       lua_sha256=hashlib.sha256(code.encode()).hexdigest(), time=time.time(),
                       gameplay_response_submitted=False, turn_activation_submitted=False)
        state['blocked_targets'].add(target)  # Reserve BEFORE write/transmission.
        record(self, name, receipt)
        try:
            raw = self.cmd(code, 'NaturalWonderPopup', 'natural-wonder-playback-'+str(proof['turn']), wait=1)
            matches = re.findall(re.escape(JSON_MARKER)+r'([^\r\n]+)', raw)
            if len(matches) != 1: raise RuntimeError('Missing/ambiguous NaturalWonder result; no replay')
            value = json.loads(matches[0])
            requested = value.get('requested') is True
            if ((MARKER in raw) != requested or value.get('coreTurn') != proof['turn'] or value.get('target') != target):
                raise RuntimeError('NaturalWonder acknowledgement mismatch; no replay')
            if requested:
                if (value.get('reason') != 'shipped_cosmetic_close' or value.get('hidden') is not False
                        or value.get('path_hidden') is not False or value.get('path_visible') is not True
                        or 'popup_stack_before' not in value or 'CSC_NATURAL_WONDER_BEFORE=' not in raw):
                    raise RuntimeError('NaturalWonder visibility/stack proof missing; no replay')
                state['acknowledgements'][target] = state['acknowledgements'].get(target, 0)+1
            elif value.get('reason') not in ('core_proof_rejected', 'ui_phase_rejected', 'source_context_missing', 'hidden', 'shipped_close_missing'):
                raise RuntimeError('Unreviewed NaturalWonder no-op; no replay')
            receipt.update(phase='acknowledged' if requested else 'verified-noop', requested=requested, native=value, raw=raw,
                           acknowledgement_count=state['acknowledgements'].get(target, 0))
            record(self, name, receipt)
            state['blocked_targets'].discard(target)
        except BaseException as error:
            receipt.update(phase='ambiguous-or-failed', error=str(error), no_control_replayed=True)
            record(self, name, receipt)
            raise
        return result

    controller.release_disaster = types.MethodType(wrapped, controller)
    return controller
