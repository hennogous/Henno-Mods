"""Passive Economic accounts/purchase journal for a shared-controller game.

This is diagnostic instrumentation, not CSC policy. The controller owns the
process, chooses the observation windows and drains the bounded journal. Import
does not import Frida or touch a process. No game functions or target-data writes
are used; Frida installs observational instruction trampolines only.
"""
import hashlib
import json
from pathlib import Path
import time

from audit_xp2_hotfix import HOTFIX_SHA, HOTFIX_TIMESTAMP, Image, XP2_IMAGE_SIZE
from district_admission_watch import dependencies


MODULE = 'GameCore_XP2_FinalRelease.dll'
MAX_RECORDS = 20000  # Per drain, not per game. Overflow invalidates the observation.
# SHA092abfbb; AI-N114/116/117 and the existing plot_purchase_observer.js qualify
# the Economic receiver, requested XY, Q8 accounts and both command handlers.
# Routine PurchasePlots/CityBuild cached XY: AI-N109/119. All are image RVAs.
POINTS = {
    'activate': 0x457120, 'routine': 0x458530,
    'cityQuote': 0x459169, 'savings': 0x45918F,
    'requestBuilt': 0x4591F3, 'commandChecked': 0x45921F,
    'commandReturned': 0x459241,
    'baseQuote': 0x681346, 'baseDebit': 0x681379,
    'baseDebitReturn': 0x68137E, 'baseAnnexReturn': 0x6813A2,
    'xp1Quote': 0x71C63E, 'xp1Debit': 0x71C671,
    'xp1DebitReturn': 0x71C676, 'xp1AnnexReturn': 0x71C69A,
    'treeInstalled': 0x3E10FD, 'selection': 0x3E0F3C,
    'purchaseInitialized': 0x55DC9F, 'setOwner': 0x616A0,
}
# Not hook sites: qualify the receiver-saving prologue and frame layout that the
# savings midpoint relies on. Reading an arbitrary readable stack word is unsafe.
GUARDS = {'receiverSave': 0x459095, 'receiverFrame': 0x4590A5}
# Optional diagnostic boundary, not a CE policy hook. REA/Ghidra identifies
# BuildQueue::PreCreateDistrict's native ABI; full1257-byte function parity is
# retained in the no-CSC campaign. Capture before any foundation writes, without
# forcing a new forecast. A successful return still needs a physical-event join.
PLACEMENT_POINTS = {'preCreateDistrict': 0x1029C0}
PLACEMENT_BODY_SHA = 'c6b12fc601d6b76ca3aa9633dbe60097f3b7acd37885ed588577e39503cca402'


def specification(binary, *, capture_placement=False):
    binary = Path(binary).resolve(strict=True)
    image = Image(binary, HOTFIX_SHA)  # Whole-file digest precedes PE/entry checks.
    if image.timestamp != HOTFIX_TIMESTAMP or image.image_size != XP2_IMAGE_SIZE:
        raise ValueError('Unexpected patched XP2 PE layout')
    if capture_placement and hashlib.sha256(image.at(PLACEMENT_POINTS['preCreateDistrict'],1257)).hexdigest()!=PLACEMENT_BODY_SHA:
        raise ValueError('Placement factory body differs from qualified native ABI')
    return dict(path=str(binary), name=MODULE, sha256=HOTFIX_SHA,
                timestamp=image.timestamp, imageSize=image.image_size,
                points={name: dict(rva=rva, prefix=image.at(rva, 32).hex())
                        for name, rva in {**POINTS, **GUARDS,
                            **(PLACEMENT_POINTS if capture_placement else {})}.items()})


class EconomySavingsWatch:
    """Observe all cities of specified AIs; keep hooks until that owner exits.

    Call drain at each controller snapshot (five turns recommended). freeze
    closes admission but leaves callbacks installed; already paired native calls
    can finish. An observer fault is a measurement failure, not a policy failure.
    Never detach from a live owner, including in exception cleanup.
    """
    def __init__(self, *, directory, binary, output, start, through, write,
                 players=(1, 2, 3, 4, 5), width, height, districts=None,capture_placement=False):
        if (not isinstance(start, int) or not isinstance(through, int) or
                not 0 <= start < through <= start + 300):
            raise ValueError('Require bounded <=300-turn observation')
        players = list(players)
        if (not players or len(players) != len(set(players)) or
                any(type(p) is not int or not 1 <= p <= 5 for p in players) or
                type(width) is not int or type(height) is not int or
                not 1 <= width <= 256 or not 1 <= height <= 256 or
                districts is not None and (type(districts) is not int or not 1 <= districts <= 4096)
                or type(capture_placement)is not bool):
            raise ValueError('Invalid original-AI/map scope')
        self.spec = specification(binary,capture_placement=capture_placement)
        self.frida = dependencies(directory)
        self.output, self.write = Path(output), write
        # Optional DB catalogue count=max(GameInfo.Districts.Index)+1, including
        # modded/replacement types. Without it choices are still recorded, but
        # cached totals remain explicitly missing rather than guessing a stride.
        self.config = dict(start=start, through=through, players=players,
                           width=width, height=height, districts=districts, maxRecords=MAX_RECORDS,
                           capturePlacement=capture_placement)
        self.owner = self.attached = self.script = self.frozen = None
        self.messages, self.rows, self.last_sequence = [], 0, 0
        script = self.output / 'economy_savings_watch.js'
        write(self.output / 'economy-savings-inputs.json', dict(
            spec=self.spec, config=self.config, diagnostic_only=True,
            frida_version=self.frida.__version__, frida_path=self.frida.__file__,
            script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
            native_calls=False, game_data_writes=False,
            limitation='Savings categories are not per-site promises; unknown lineage stays unknown'))

    def attach(self, owner, loaded_modules):
        loaded = loaded_modules.get(MODULE, {})
        if self.attached is not None or owner.poll() is not None:
            raise RuntimeError('Expected fresh observer and live controller-owned process')
        if (loaded.get('sha256') != HOTFIX_SHA or
                Path(loaded.get('path', '')).resolve() != Path(self.spec['path'])):
            raise ValueError('Loaded module differs from explicit Economic binary')
        self.owner = owner
        self.attached = self.frida.attach(owner.pid)
        self.script = self.attached.create_script(
            (self.output / 'economy_savings_watch.js').read_text(encoding='utf-8'))
        self.script.on('message', self._message)
        self.script.load()
        status = self.script.exports_sync.init(self.spec, self.config)
        self.write(self.output / 'economy-savings-ready.json', status)
        expected=len(POINTS)+(len(PLACEMENT_POINTS)if self.config['capturePlacement']else 0)
        if not status['installed'] or status['hooks'] != expected:
            raise RuntimeError('Economic hook qualification failed')
        self.script.exports_sync.start()

    def _message(self, message, data):
        # Normal data travel through drain(); any asynchronous Frida message is
        # unexpected and retained as a diagnostic failure, bounded against spam.
        if len(self.messages) < 64:
            self.messages.append(message)

    def window(self, start, through):
        if self.script is None or self.frozen is not None:
            raise RuntimeError('Cannot advance unready/frozen Economic observer')
        self.script.exports_sync.window(start, through)

    def drain(self):
        if self.script is None:
            return None
        batch = self.script.exports_sync.drain()
        # A sequence gap/duplicate means the journal cannot explain the whole
        # window. Persist rows before reporting that failure for later diagnosis.
        with (self.output / 'economy-savings.ndjson').open('a', encoding='utf-8') as log:
            for row in batch['records']:
                log.write(json.dumps(row, separators=(',', ':')) + '\n')
                if row['sequence'] != self.last_sequence + 1:
                    raise RuntimeError('Economic journal sequence gap')
                self.last_sequence = row['sequence']
                self.rows += 1
        self.write(self.output / 'economy-savings-progress.json',
                   dict(rows=self.rows, **{k: v for k, v in batch.items() if k != 'records'}))
        if batch['faults'] or batch['stopReason']:
            raise RuntimeError('Economic observer fault; retained journal is partial')
        return batch

    def freeze(self):
        if self.script is None or self.frozen is not None:
            return
        deadline = time.monotonic() + 5
        while True:
            state = self.script.exports_sync.freeze()
            self.write(self.output / 'economy-savings-frozen.json', state)
            if state['frozen']:
                self.frozen = state
                self.drain()
                return
            if time.monotonic() >= deadline:
                raise RuntimeError('Economic native pairs active; retain exact process owner')
            time.sleep(.05)

    def after_exit(self):
        if self.owner is not None and self.owner.poll() is None:
            raise RuntimeError('Never detach Economic observer from live owner')
        self.write(self.output / 'economy-savings-messages.json', self.messages)
        if self.attached is not None:
            try:
                self.attached.detach()
            except self.frida.InvalidOperationError:
                pass  # Process exit may already have detached the session.
            self.attached = None

    def qualify(self):
        if (not self.frozen or not self.frozen['frozen'] or self.frozen['active'] or
                self.frozen['faults'] or self.frozen['stopReason'] or self.messages):
            raise RuntimeError('Incomplete/faulted Economic observation')
