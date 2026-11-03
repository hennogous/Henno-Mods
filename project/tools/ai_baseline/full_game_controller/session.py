"""Shared session boundaries around the unchanged finite-play controller.

No native work on import. Launch strategy, scientific source gate, observers,
preferences and package restoration are explicit adapter callbacks. An issued
operation is reserved on disk BEFORE transmission and never retried here.
"""
import hashlib
import json
import os
import re
import time
from pathlib import Path

from .discovery import discover_contexts
from .transport import MissingAcknowledgment


class SessionError(RuntimeError):
    pass


class NativeSession:
    def __init__(self, output, controller, *, inventory, hold, write,
                 discover=discover_contexts, clock=time.monotonic,
                 sleep=time.sleep):
        self.output = Path(output)
        self.controller = controller
        self.inventory = inventory
        self.hold = hold
        self.write = write
        self.discover = discover
        self.clock = clock
        self.sleep = sleep
        self.owner = None
        self.eligible = False
        self.closed = False

    def issue_once(self, key, code, context, *, label=None):
        if self.closed or self.owner is None or self.owner.poll() is not None:
            raise SessionError('No live held session owner')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            raise ValueError('Invalid session operation key')
        path = self.output / 'session-operations' / (key + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        record = dict(key=key, context=context, label=label or key,
                      lua_sha256=hashlib.sha256(code.encode()).hexdigest(),
                      issued_at_most_once=True, reserved_unix=time.time())
        # Exclusive create + fsync: an ambiguous request or restarted driver
        # cannot silently reserve the same operation again.
        with path.open('x', encoding='utf-8') as stream:
            json.dump(record, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            return self.controller.cmd(code, context, label or key, check=True)
        except (MissingAcknowledgment, OSError, EOFError) as error:
            self.write(path.with_name(key + '-ack-warning.json'),
                       dict(error=str(error), no_resend=True,
                            postcondition_required=True))
            # Only a fresh readiness/exit postcondition may settle ambiguity.
            return None

    def start(self, launch=None, *, attach_pid=None):
        if self.owner is not None or self.closed:
            raise SessionError('Session already started or closed')
        rows = self.inventory()
        if attach_pid is None:
            if rows:
                raise SessionError('Foreign native/Tuner owner; preserve it')
            if launch is None:
                raise ValueError('Launch callback required')
            # Launch callback owns direct-vs-Steam bootstrap policy. It must
            # return the actual held process, not an exited bootstrap PID.
            process = launch()
            pid = process.pid
        else:
            if launch is not None:
                raise ValueError('Attach and launch are mutually exclusive')
            if len(rows) != 1 or rows[0]['pid'] != attach_pid:
                raise SessionError('Attach requires the sole declared native owner')
            pid = attach_pid
        # Keep the callback's actual held launch object. Reopening a PID here
        # would lose its original creation identity across a fast exit/reuse.
        self.owner = process if attach_pid is None and hasattr(process, 'identity') else self.hold(pid)
        self.write(self.output / 'session-owner.json', self.owner.identity)
        if attach_pid is not None:
            expected = rows[0].get('identity')
            if expected is None or self.owner.identity != expected:
                raise SessionError('Attach creation/path identity changed since inventory')
        if self.owner.poll() is not None:
            raise SessionError('Held native owner already exited')
        if attach_pid is None and process.poll() is not None:
            raise SessionError('Launch process exited before ownership was established')
        self.controller.game_pid = pid
        self.controller.wait = self.wait_context
        return self.owner

    def wait_context(self, context, seconds=240):
        deadline = self.clock() + seconds
        while self.clock() < deadline:
            if self.owner is None or self.owner.poll() is not None:
                raise SessionError('Exact held native process exited')
            try:
                _, states = self.discover(required=context)
                if context in states:
                    return
            except (OSError, EOFError, RuntimeError):
                pass  # Read-only discovery only; never resend a mutation.
            self.sleep(.5)
        raise TimeoutError('Native context not ready: ' + context)

    def ready_after_issue(self, turn, contexts, *, eligibility, timeout=300):
        self.eligible = False
        # One total context-readiness budget, not a full timeout per context.
        deadline = self.clock() + timeout
        for context in contexts:
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise TimeoutError('Load/host readiness budget exhausted')
            self.wait_context(context, remaining)
        self.controller.ready(turn, 'session-source-ready')
        # Caller owns complete parity/scientific eligibility. No field masking,
        # movement normalization, implicit rebase or gameplay restoration here.
        proof = eligibility()
        if proof is not True:
            raise SessionError('Caller source eligibility was not verified')
        self.eligible = True
        self.controller.last_interval_turn = turn
        self.write(self.output / 'session-source-ready.json',
                   dict(verified=True, turn=turn, contexts=list(contexts),
                        caller_eligibility_verified=True, load_ack_is_readiness=False))

    def issue_load_once(self, source, *, sha256, native_directory, turn):
        source = Path(source).resolve()
        if source.parent != Path(native_directory).resolve() or source.suffix != '.Civ6Save':
            raise SessionError('Load requires a supported native Saves/Single path')
        if hashlib.sha256(source.read_bytes()).hexdigest() != sha256:
            raise SessionError('Load input hash mismatch')
        self.write(self.output / 'session-load-input.json',
                   dict(source=str(source), sha256=sha256, turn=turn))
        code = ('Automation.SetAutoStartEnabled(true);Network.LoadGame('
                + json.dumps(str(source)) + ',ServerType.SERVER_TYPE_NONE);')
        self.issue_once('load', code, 'MainMenu')

    def load_once(self, source, *, sha256, native_directory, turn, contexts,
                  eligibility, timeout=300):
        self.issue_load_once(source, sha256=sha256, native_directory=native_directory, turn=turn)
        self.ready_after_issue(turn, contexts, eligibility=eligibility, timeout=timeout)

    def close(self, *, restore_preferences, restore_package=lambda: None,
              before_menu=lambda: None, after_native_exit=lambda: None,
              exit_timeout=60):
        if self.closed:
            raise SessionError('Session already closed')
        # A freeze/restoration failure must not be described as complete. Keep
        # observer/native alive for reconciliation rather than detach unsafely.
        before_menu()
        if self.owner is None:
            raise SessionError('Cannot clean up an unowned process')
        if self.owner.poll() is not None:
            raise SessionError('Native exited before preference restoration')
        _, states = self.discover(required='MainMenu')
        if 'GameCore_Tuner' in states or 'PlotInfo' in states:
            self.issue_once('menu', 'Events.ExitToMainMenu();', 'PlotInfo')
        self.wait_context('MainMenu', 180)
        restore_preferences()
        self.issue_once('exit', 'assert(type(ExitOK)=="function");ExitOK();', 'FrontEndPopup')
        deadline = self.clock() + exit_timeout
        while self.owner.poll() is None and self.clock() < deadline:
            self.sleep(.5)
        code = self.owner.poll()
        if code is None:
            raise SessionError('Held native still alive; no package restoration')
        self.write(self.output / 'session-native-exit.json',
                   dict(identity=self.owner.identity, exit_code=code,
                        supported_exit_requested=True))
        after_native_exit()
        if self.inventory():
            raise SessionError('Native/Tuner owner remains; no package restoration')
        restore_package()
        self.closed = True
        self.write(self.output / 'session-closed.json',
                   dict(verified=code == 0, native_exit_code=code,
                        owners_absent=True, preferences_verified=True,
                        package_callback_completed=True))
        self.owner.close()
        if code != 0:
            raise SessionError('Native exit was nonzero; restoration completed, no successful run claim')
