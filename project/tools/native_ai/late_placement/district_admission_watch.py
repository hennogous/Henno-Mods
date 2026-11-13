"""Optional read-only native admission diagnostic for a controller-owned replay.

This is deliberately outside CSC policy. It follows a live Quarter request from
CityBuild.ReceiveContract through UnitRequestContract.Validate and CanZone, then
records the requirements that can reject it before the CSV says SUBMITTED. It
never calls a game function or changes a bid, argument, return value or game data.
Frida supplies observational entry/exit trampolines, not a second AI publisher.

The parent replay owns all game actions. Importing this module neither imports
Frida nor attaches to anything. Both the existing dependency directory and exact
binary are explicit opt-in inputs; the patched XP2 SHA below is the only target.
"""
import importlib
import hashlib
from pathlib import Path
import sys
import time

from audit_xp2_hotfix import HOTFIX_SHA, HOTFIX_TIMESTAMP, Image, XP2_IMAGE_SIZE


MODULE = 'GameCore_XP2_FinalRelease.dll'
FRIDA_VERSION = '17.24.3'
MAX_RECORDS = 10000
# Current SHA092abfbb, with the complete relevant bodies byte-qualified against
# reference SHA324c51e9 in csc-ai-district-admission-20261113/binary-qualification.
# RVAs are image-relative, not absolute runtime addresses. The full file digest
# is checked first; every 32-byte entry is rechecked in memory before any hook.
POINTS = {
    'receive': 0x3E9500,
    'validate': 0x3FA8E0,
    'zone': 0xF97B0,
    'districtCount': 0x11EB20,
    'allowedCount': 0x11EAE0,
}


def specification(binary):
    binary = Path(binary).resolve(strict=True)
    image = Image(binary, HOTFIX_SHA)
    if image.timestamp != HOTFIX_TIMESTAMP or image.image_size != XP2_IMAGE_SIZE:
        raise ValueError('Unexpected patched XP2 PE layout')
    return dict(path=str(binary), name=MODULE, sha256=HOTFIX_SHA,
                timestamp=image.timestamp, imageSize=image.image_size,
                points={name: dict(rva=rva, prefix=image.at(rva, 32).hex())
                        for name, rva in POINTS.items()})


def dependencies(directory):
    """Only reuse the caller's already installed, exercised Frida package."""
    directory = Path(directory).resolve(strict=True)
    if not (directory / 'frida/__init__.py').is_file():
        raise ValueError('Explicit Frida dependency directory is missing its package')
    sys.path.insert(0, str(directory))
    module = importlib.import_module('frida')
    if (module.__version__ != FRIDA_VERSION or
            not Path(module.__file__).resolve().is_relative_to(directory)):
        raise ValueError('Require explicit existing Frida 17.24.3 dependency')
    return module


def validate_options(enabled, directory, binary):
    if enabled != bool(directory and binary) or (not enabled and (directory or binary)):
        raise ValueError('--admission-probe requires both --frida-deps and --admission-binary')


class AdmissionWatch:
    """Retain hooks from the inactive boundary until the exact owner exits.

    A probe fault stops recording and invalidates this measurement; it does not
    disable CSC policy or alter native decisions. Before returning to the menu,
    freeze at a controller boundary and wait for paired callbacks to drain. Never
    detach an observer from a live game in a cleanup exception path.
    """
    def __init__(self, *, directory, binary, output, start, through, write):
        if not 0 < through - start <= 30:
            raise ValueError('Admission observation requires a short replay window')
        self.frida = dependencies(directory)
        self.spec = specification(binary)
        self.output, self.write = Path(output), write
        self.config = dict(start=start, through=through, maxRecords=MAX_RECORDS)
        self.attached = self.script = self.owner = self.frozen = None
        self.messages = []
        write(self.output / 'admission-inputs.json', dict(
            spec=self.spec, config=self.config, diagnostic_only=True,
            frida_version=self.frida.__version__, frida_path=self.frida.__file__,
            script_sha256=hashlib.sha256((self.output/'district_admission_watch.js').read_bytes()).hexdigest(),
            score_or_game_data_writes=False, native_calls=False))

    def attach(self, owner, loaded_modules):
        if self.attached is not None or owner.poll() is not None:
            raise RuntimeError('Expected fresh probe and live controller-owned process')
        loaded = loaded_modules.get(MODULE, {})
        if (loaded.get('sha256') != HOTFIX_SHA or
                Path(loaded.get('path', '')).resolve() != Path(self.spec['path'])):
            raise ValueError('Loaded module proof differs from explicit admission binary')
        self.owner = owner
        self.attached = self.frida.attach(owner.pid)
        self.script = self.attached.create_script(
            (self.output/'district_admission_watch.js').read_text(encoding='utf-8'))
        self.script.on('message', self._message)
        self.script.load()
        status = self.script.exports_sync.init(self.spec, self.config)
        self.write(self.output / 'admission-ready.json', status)
        if not status['installed'] or status['hooks'] != len(POINTS):
            raise RuntimeError('Admission hook qualification failed')
        self.script.exports_sync.start()

    def _message(self, message, data):
        # JS uses no send() stream. Any unexpected message is retained as a fault,
        # with a bounded host list even if an engine repeatedly reports an error.
        if len(self.messages) < 64:
            self.messages.append(message)

    def window(self, start, through):
        if self.frozen is not None or self.script is None:
            raise RuntimeError('Cannot advance an unready/frozen admission observer')
        self.script.exports_sync.window(start, through)

    def freeze(self):
        if self.frozen is not None or self.script is None:
            return
        deadline = time.monotonic() + 5
        while True:
            state = self.script.exports_sync.freeze()
            self.write(self.output / 'admission-frozen.json', state)
            if state['frozen']:
                self.frozen = state
                return
            if time.monotonic() >= deadline:
                raise RuntimeError('Admission callback still active; preserve exact native owner')
            time.sleep(.05)

    def after_exit(self):
        if self.owner is not None and self.owner.poll() is None:
            raise RuntimeError('Never detach admission hooks from a live owner')
        self.write(self.output / 'admission-messages.json', self.messages)
        if self.attached is not None:
            # Process exit releases target trampolines. No unload/detach is sent
            # while native instructions could still be using them.
            try:
                self.attached.detach()
            except self.frida.InvalidOperationError:
                pass  # An exited process may already have detached its session.
            self.attached = None

    def qualify(self):
        if (not self.frozen or not self.frozen['frozen'] or self.frozen['active'] or
                self.frozen['stopReason'] or self.frozen['faults'] or self.messages):
            raise RuntimeError('Incomplete/faulted admission measurement; not an AI-policy failure')
