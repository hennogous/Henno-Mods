"""Explicit mutating-score profile; retain Frida references until held native exit.

No native work on import. The worker never unloads a script or detaches a live
process, including after setup, RPC or scientific validation failures.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(HERE.parent)]
from full_game_controller.windows_process import HeldProcess

PROFILE = 'quarter-placement-choice-v2'
SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
FUNCTIONS = {
    'DistrictNetValue': (0x52a440, '8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'),
    'CalculateDistrictValues': (0x3dfee0, '4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'),
    'GetBestDistrict': (0x3e4a50, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'),
    'PresentValueOf': (0x3e7f40, '4d63d84c8bd2488bc14183fbff750833c9488bc2890ac34d85c9744d8b81d804'),
}
WRITE_LOCK = threading.RLock()


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    # Frida's message thread and the RPC loop may report the same fault together.
    with WRITE_LOCK:
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name+'.tmp')
        temporary.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
        temporary.replace(path)


def manifest(root):
    root = Path(root)
    return {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}


def validate_contract(spec, config):
    fixed = dict(profile=PROFILE, maxChanges=128, maxRecords=512,
                 session=7, epoch=1, version=2, originalHuman=False, currentHuman=False,
                 mappingVerified=True, snapshotVerified=True)
    dynamic = {'mode','player','city','districtType','districtIndex','districtCount','districtIndexLimit',
               'plot','plotX','plotY','mapWidth','mapHeight','deltaQ8','baselineGapQ8','marginQ8'}
    if not isinstance(config, dict) or set(config) != set(fixed) | dynamic:
        raise ValueError('Exact explicit extension configuration required')
    if any(type(config[k]) is not type(v) or config[k] != v for k, v in fixed.items()):
        raise ValueError('Unreviewed extension scope/budget/role')
    if config['mode'] not in ('baseline', 'treatment'):
        raise ValueError('Explicit baseline/treatment arm required')
    numeric = dynamic - {'mode','districtType'}
    if any(type(config[k]) is not int for k in numeric): raise ValueError('Integer policy fields required')
    if (not 1 <= config['player'] <= 61 or not 0 <= config['city'] <= 2147483647
            or not re.fullmatch(r'DISTRICT_CSC_[A-Z]+_QUARTER',config['districtType'])
            or not 1 <= config['mapWidth'] <= 256 or not 1 <= config['mapHeight'] <= 256
            or not 0 <= config['baselineGapQ8'] < 1048576 or config['marginQ8'] != 256
            or config['deltaQ8'] != config['baselineGapQ8']+config['marginQ8']
            or not 0 < config['deltaQ8'] <= 1048576):
        raise ValueError('Invalid scoped policy, gap or declared margin')
    if config['mode']=='baseline':
        if (config['plot'],config['plotX'],config['plotY'],config['baselineGapQ8']) != (-1,-1,-1,0):
            raise ValueError('Baseline must observe all candidate sites without a treatment gap')
    elif (not 0 <= config['plotX'] < config['mapWidth'] or not 0 <= config['plotY'] < config['mapHeight']
            or config['plot'] != config['plotY']*config['mapWidth']+config['plotX']):
        raise ValueError('Treatment requires one explicit mapped site')
    if (any(type(config[k]) is not int for k in ('districtIndex', 'districtCount', 'districtIndexLimit'))
            or not 0 < config['districtIndex'] < config['districtCount'] == config['districtIndexLimit'] <= 4096):
        raise ValueError('Positive verified loaded district mapping required')
    rows = spec.get('functions', [])
    if (len(rows) != 4 or any(type(r.get('rva')) is not int for r in rows)
            or {r['name']: (r['rva'], r['bytes']) for r in rows} != FUNCTIONS
            or spec.get('sha256') != SHA or spec.get('timestamp') != 1719431003
            or spec.get('image_size') != 12976128 or not isinstance(spec.get('path'), str) or not spec['path']):
        raise ValueError('Unreviewed extension native build/fingerprints')


def validate_proof(proof, identity, spec):
    module = proof.get('module', {})
    if (proof.get('verified') is not True or proof.get('identity') != identity or proof.get('sha256') != SHA
            or str(module.get('FileName', '')).lower() != spec['path'].lower()
            or module.get('size') != spec['image_size']):
        raise ValueError('Loaded-module proof does not match held owner/build')


def validate_status(status, spec, config, *, enabled, allow_partial=False):
    installation_ok = (status.get('installed') is True and type(status.get('hooks')) is int and status['hooks'] == 4)
    if allow_partial and not enabled:
        installation_ok = (type(status.get('installed')) is bool and type(status.get('hooks')) is int and 0 <= status['hooks'] <= 4)
    if (status.get('profile') != PROFILE or status.get('read_only') is not False
            or not installation_ok or status.get('enabled') is not enabled
            or str(status.get('module_path', '')).lower() != spec['path'].lower()
            or status.get('module_size') != spec['image_size'] or status.get('loaded_timestamp') != spec['timestamp']
            or status.get('validated_entry_fingerprints') != spec['functions'] or status.get('config') != config):
        raise ValueError('Extension status/module/config identity mismatch')


def validate_snapshot(value, config, *, frozen=False, allow_faults=False):
    if value.get('profile') != PROFILE or value.get('read_only') is not False:
        raise ValueError('Snapshot must declare the explicit mutating profile')
    stats, rows = value.get('stats'), value.get('records')
    if not isinstance(stats, dict) or not isinstance(rows, list): raise ValueError('Malformed extension snapshot')
    for k in ('callbacks', 'admitted', 'changed', 'errors', 'records', 'suppressed', 'active', 'mode'):
        if type(stats.get(k)) is not int or stats[k] < 0: raise ValueError('Malformed extension counter: '+k)
    if stats['mode'] > 2 or stats['records'] != len(rows) or len(rows) > 512:
        raise ValueError('Invalid mode/record bounds')
    for row in rows:
        if (not isinstance(row, dict) or row.get('k') not in ('net', 'cache', 'best', 'pv')
                or row.get('player') != config['player'] or row.get('city') != config['city']):
            raise ValueError('Record outside declared city/boundary scope')
        if any(type(row.get(k)) is not int or not -2147483648 <= row[k] <= 2147483647
               for k in ('player','city','district','plot','x','y','base','result','reason','eligible')):
            raise ValueError('Malformed native record packet')
        if row['eligible'] not in (0,1): raise ValueError('Invalid native row flag')
        if row['k'] != 'net' and row['base'] != row['result']:
            raise ValueError('Only NetValue output can carry an adjustment')
        if row['k'] == 'net':
            if any(type(row.get(k)) is not int or not -2147483648 <= row[k] <= 2147483647
                   for k in ('district', 'plot', 'x', 'y', 'base', 'result', 'reason', 'eligible')):
                raise ValueError('Malformed native net record')
            if row['district'] != config['districtIndex'] or (config['mode']=='treatment' and
                    (row['plot'],row['x'],row['y']) != (config['plot'],config['plotX'],config['plotY'])):
                raise ValueError('Net record outside exact candidate')
    if frozen and (stats['mode'] != 0 or stats['active'] != 0):
        raise RuntimeError('Freeze did not disable and drain native invocations')
    reservations=value.get('reservations',[])
    if (not isinstance(reservations,list) or len(reservations)>37
            or type(value.get('reservationCaptureCount',0)) is not int
            or value.get('reservationCaptureCount',0)<0):
        raise ValueError('Malformed bounded reservation metadata')
    for item in reservations:
        if (not isinstance(item,dict) or any(type(item.get(k)) is not int for k in ('plot','controller','score','cacheScore'))
                or not 0 <= item['plot'] < config['mapWidth']*config['mapHeight']):
            raise ValueError('Invalid reservation metadata row')
    if not allow_faults:
        changes = [r for r in rows if r['k'] == 'net' and r['result'] != r['base']]
        if (value.get('fatal') or stats['errors'] or stats['active']
                or stats['changed'] > (0 if config['mode'] == 'baseline' else config['maxChanges'])
                or len(changes) != stats['changed']
                or any(r['result']-r['base'] != config['deltaQ8'] or r['base'] == -2559744 or r['base'] == 0
                       or r['reason'] != 0 or r['eligible'] != 1 for r in changes)):
            raise RuntimeError('Scientific extension fault or mutation contract violation')
    return bool(value.get('saturated') or stats['suppressed'] or stats['records'] >= 512)


class NativeExtension:
    """One attach/start; freeze even after faults; release only after held exit."""
    def __init__(self, output, owner, *, script, spec, config, dependencies, loaded_module, python=None):
        self.output = Path(output); self.owner = owner
        self.spec, self.config = read(spec), read(config)
        validate_contract(self.spec, self.config)
        validate_proof(read(loaded_module), owner.identity, self.spec)
        if owner.poll() is not None: raise RuntimeError('Held native already exited')
        self.output.mkdir(parents=True, exist_ok=False)
        for name, path in [('trace.js', script), ('kernel.c', HERE/'kernel.c'), ('native-spec.json', spec),
                           ('observer-config.json', config), ('loaded-module.json', loaded_module)]:
            (self.output/name).write_bytes(Path(path).read_bytes())
        write(self.output/'native-owner.json', owner.identity)
        self.inputs = {name: sha(self.output/name) for name in ('trace.js', 'kernel.c', 'native-spec.json', 'observer-config.json', 'loaded-module.json', 'native-owner.json')}
        write(self.output/'trace-inputs.json', self.inputs)
        self.dependencies = Path(dependencies).resolve()
        write(self.output/'trace-dependencies.json', manifest(self.dependencies))
        self.process = None; self.seq = 0; self.frozen = False; self.started = False
        self.python = Path(python or sys._base_executable)

    def _intent(self, name, text):
        with (self.output/name).open('x', encoding='utf-8') as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())

    def _wait(self, name, *, check_errors=True, seconds=30):
        deadline = time.monotonic()+seconds
        while time.monotonic() < deadline:
            if (self.output/name).exists(): return read(self.output/name)
            if self.owner.poll() is not None: raise RuntimeError('Held native exited before extension acknowledgement')
            if check_errors and (self.output/'trace-daemon-error.json').exists(): raise RuntimeError('Extension daemon fault; retained until native exit')
            if self.process is not None and self.process.poll() is not None: raise RuntimeError('Extension worker exited before native')
            time.sleep(.1)
        raise TimeoutError('Unconfirmed extension action; no replay: '+name)

    def attach_disabled(self):
        if self.process is not None: raise RuntimeError('Extension attach cannot repeat')
        if any(sha(self.output/n) != h for n, h in self.inputs.items()): raise RuntimeError('Archived extension inputs changed')
        with (self.output/'trace-daemon.log').open('xb') as log:
            self.process = subprocess.Popen([str(self.python), '-B', str(Path(__file__).resolve()), '--worker',
                '--output', str(self.output), '--dependencies', str(self.dependencies), '--owner-tag', 'csc-native-district-extension'],
                stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        ready = self._wait('trace-ready.json')
        if ready.get('identity') != self.owner.identity or ready.get('frida_version') != '17.24.3': raise ValueError('Worker identity/version mismatch')
        validate_status(ready['status'], self.spec, self.config, enabled=False)
        return ready

    def start(self):
        if self.started or self.frozen: raise RuntimeError('Extension start cannot repeat or follow freeze')
        self.started = True; self._intent('trace-start.request', 'once')
        result = self._wait('trace-started.json')
        validate_status(result['status'], self.spec, self.config, enabled=True)
        return result

    def snapshot(self, label):
        if not self.started or self.frozen or not re.fullmatch(r'[A-Za-z0-9_-]+', label): raise ValueError('Invalid snapshot phase/label')
        self.seq += 1; token = str(self.seq).zfill(3)+'-'+label
        self._intent('snapshot-intent-'+token+'.json', json.dumps(dict(token=token, read_only=False, profile=PROFILE)))
        self._intent('trace-snapshot.request', token)
        result = self._wait('trace-snapshot-'+token+'.json')
        return result, validate_snapshot(result, self.config)

    def before_menu(self):
        if self.frozen: return
        if self.process is None:
            write(self.output/'trace-no-worker-freeze.json', dict(disabled_without_hooks=True, worker_started=False))
            self.frozen = True; return
        self._intent('trace-freeze.request', 'cleanup-once')
        result = self._wait('trace-counts.json', check_errors=False)
        if result.get('disabled_without_hooks') is True:
            if result.get('identity') != self.owner.identity or result.get('script_load_attempted') is not False:
                raise ValueError('Unproven no-hooks freeze')
        else:
            validate_status(result['status'], self.spec, self.config, enabled=False, allow_partial=True)
            validate_snapshot(result['snapshot'], self.config, frozen=True, allow_faults=True)
        self.frozen = True

    def after_native_exit(self):
        if self.owner.poll() is None: raise RuntimeError('Native still alive; keep extension retained')
        if self.process is None: raise RuntimeError('Extension worker was not started')
        self.process.wait(timeout=30)
        value = read(self.output/'trace-daemon-exit.json')
        if (value.get('identity') != self.owner.identity or value.get('native_absent') is not True
                or value.get('explicit_detach') is not False or self.process.returncode != 0):
            raise RuntimeError('Extension retained-exit proof failed')
        return value


def worker(args):
    out = args.output; held = None; session = None; script = None
    expected = None; load_attempted = False; fault = False; started = False; frozen = False; freeze_attempted = False
    def report_error():
        nonlocal fault
        fault = True
        write(out/'trace-daemon-error.json', dict(traceback=traceback.format_exc(), retain_until_native_exit=True, script_load_attempted=load_attempted))
    try:
        try:
            expected = read(out/'native-owner.json'); held = HeldProcess(expected['pid'])
            if held.identity != expected:
                held.close(); held = None
                raise RuntimeError('Exact held identity mismatch; no attach attempted')
            if held.poll() is not None: raise RuntimeError('Held native already exited')
            spec, config = read(out/'native-spec.json'), read(out/'observer-config.json')
            validate_contract(spec, config); validate_proof(read(out/'loaded-module.json'), expected, spec)
            if any(sha(out/n) != h for n, h in read(out/'trace-inputs.json').items()): raise RuntimeError('Archived worker inputs changed')
            if manifest(args.dependencies) != read(out/'trace-dependencies.json'): raise RuntimeError('Frida dependency pins changed')
            if sha(spec['path']) != SHA: raise RuntimeError('Native file hash changed')
            sys.path.insert(0, str(args.dependencies)); import frida
            if frida.__version__ != '17.24.3' or not Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve()):
                raise RuntimeError('Require pinned Frida17.24.3 from declared dependency root')
            source = (out/'trace.js').read_text(encoding='utf-8-sig')
            if any(source.count(token) != 1 for token in ('__SPEC__', '__CONFIG__', '__KERNEL_C__')): raise ValueError('Explicit template contract missing')
            source = source.replace('__SPEC__', json.dumps(spec)).replace('__CONFIG__', json.dumps(config)).replace('__KERNEL_C__', json.dumps((out/'kernel.c').read_text(encoding='utf-8-sig')))
            session = frida.attach(expected['pid'])
            def detached(*details):
                try: alive = held.poll() is None
                except OSError: alive = None  # Exit notification can race handle close.
                receipt = dict(identity=expected, details=str(details), native_alive=alive, time=time.time())
                with (out/'detachments.ndjson').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(receipt)+'\n'); stream.flush(); os.fsync(stream.fileno())
                write(out/'detachment.json', receipt)
            session.on('detached', detached)
            script = session.create_script(source)
            def received(message, data):
                nonlocal fault
                write(out/'trace-message.json', message)
                if message.get('type') == 'error':
                    fault = True; write(out/'trace-daemon-error.json', dict(message=message, retain_until_native_exit=True))
            script.on('message', received)
            load_attempted = True; script.load()
            status = script.exports_sync.status(); validate_status(status, spec, config, enabled=False)
            write(out/'trace-ready.json', dict(identity=expected, daemon_pid=os.getpid(), frida_version=frida.__version__, status=status))
        except BaseException:
            report_error()
        # Keep processing freeze after setup/RPC/scientific errors. Never abandon
        # RPC and leave a possibly mutating callback running solely due to a fault.
        while held is not None and held.poll() is None:
            try:
                if (out/'trace-freeze.request').exists() and not freeze_attempted:
                    freeze_attempted = True
                    if not load_attempted:
                        write(out/'trace-counts.json', dict(identity=expected, disabled_without_hooks=True, script_load_attempted=False))
                    else:
                        value = script.exports_sync.freeze()
                        status = script.exports_sync.status()
                        validate_status(status, spec, config, enabled=False, allow_partial=True)
                        validate_snapshot(value, config, frozen=True, allow_faults=True)
                        write(out/'trace-counts.json', dict(snapshot=value, status=status))
                    frozen = True
                if not frozen and not fault and (out/'trace-start.request').exists() and not started:
                    started = True
                    value = script.exports_sync.start(); status = script.exports_sync.status()
                    validate_status(status, spec, config, enabled=True)
                    write(out/'trace-started.json', dict(result=value, status=status))
                request = out/'trace-snapshot.request'
                if not frozen and not fault and request.exists():
                    token = request.read_text(encoding='utf-8')
                    if not re.fullmatch(r'[0-9]{3}-[A-Za-z0-9_-]+', token): raise ValueError('Invalid snapshot token')
                    value = script.exports_sync.snapshot()
                    write(out/('trace-snapshot-'+token+'.json'), value); request.unlink()
            except BaseException:
                report_error()
            time.sleep(.2)
    finally:
        # Strong references remain live until the exact held process has ended.
        while held is not None and held.poll() is None: time.sleep(.5)
        absent = held is not None and held.poll() is not None
        identity = held.identity if held else expected
        if held is not None: held.close()
        write(out/'trace-daemon-exit.json', dict(identity=identity, native_absent=absent, explicit_detach=False,
              script_load_attempted=load_attempted, diagnostic_fault=fault, time=time.time()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    parser.add_argument('--owner-tag', choices=('csc-native-district-extension',), required=True)
    worker(parser.parse_args())


if __name__ == '__main__': main()
