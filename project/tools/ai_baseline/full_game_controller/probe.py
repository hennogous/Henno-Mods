"""Small probe controller adapter; no dated Desktop executor imports.

Use NativeSession for launch/load/cleanup and the unchanged finite core for play.
Readers, source parity, treatments and optional observers remain caller-owned.
"""
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from .controller import make_controller
from .discovery import discover_contexts


ATOMIC_JSON_ATTEMPTS = 5
ATOMIC_JSON_RETRY_SECONDS = .1


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2) + '\n'
    temporary = None
    try:
        # Unique same-directory files prevent concurrent publishers from sharing
        # a .tmp name. Closed before replacement for Windows sharing semantics.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=path.parent, prefix='.' + path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        for attempt in range(ATOMIC_JSON_ATTEMPTS):
            try:
                temporary.replace(path)
                return
            except PermissionError:
                if attempt == ATOMIC_JSON_ATTEMPTS - 1:
                    raise
                time.sleep(ATOMIC_JSON_RETRY_SECONDS)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _user_root(value):
    # The finite controller reads diplomatic evidence under USER/Logs. An
    # explicit native user directory is authoritative; a default must identify
    # an existing Windows game/log directory, never the output or current path.
    if value is None:
        local = os.environ.get('LOCALAPPDATA')
        if not local or not Path(local).is_absolute():
            raise ValueError('Pass user_root explicitly: absolute LOCALAPPDATA is unavailable')
        root = Path(local) / 'Firaxis Games' / "Sid Meier's Civilization VI"
        if not root.is_dir() or not (root / 'Logs').is_dir():
            raise ValueError('Pass user_root explicitly: LOCALAPPDATA has no existing Civ VI Logs directory')
    else:
        root = Path(value)
        if not root.is_absolute() or not root.is_dir():
            raise ValueError('user_root must be an absolute existing native user directory')
    return root.resolve()


class Diagnostics:
    def __init__(self, output, user_root=None):
        self.output = Path(output)
        self.USER = _user_root(user_root)

    write = staticmethod(write_json)

    @staticmethod
    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def journal(self, event, **fields):
        with (self.output / 'controller-journal.ndjson').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(event=event, **fields)) + '\n')
            stream.flush()
            os.fsync(stream.fileno())

    def checkpoint(self, label):
        self.journal('checkpoint', label=label)


def boundary_decision(turn, target, inactive):
    if turn > target:
        raise RuntimeError('Native autoplay overrun')
    if turn == target:
        return 'done', inactive
    if inactive >= 3:
        raise RuntimeError('Native inactive below target')
    return 'wait', inactive + 1


class ProbeInterfaces:
    def __init__(self, output):
        self.seq = 0
        self.required_state = 'GameCore_Tuner'
        self.state = {}

    def capture(self, label):
        """Archive the shared read-only phase proof used by ownership handoff.

        Small probes have no experiment-specific world snapshot. Their capture
        explicitly records that limited scope rather than requiring the full
        native diagnostic payload of a particular experiment.
        """
        if not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', label):
            raise ValueError('Invalid probe capture label')
        value = dict(read_only=True, scope='shared-controller-phase',
                     phase=self.state_read(label + '-phase'))
        self.diagnostics.write(self.root / 'captures' / (label + '.json'), value)
        self.diagnostics.journal('readonly-probe-capture', label=label,
                                 scope=value['scope'], phase=value['phase'])
        return value


def make_probe_controller(output, *, user_root=None):
    """Construct without native I/O; bind the actual user directory for log reads."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    diagnostics = Diagnostics(output, user_root=user_root)
    Controller = make_controller(ProbeInterfaces, diagnostics=diagnostics,
                                 boundary_decision=boundary_decision,
                                 tuner_port=4318, state_discovery=discover_contexts)
    return Controller(output)
