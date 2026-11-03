"""Bounded observer process adapter for NativeSession; no native work on import.

Promotes the proven retained-daemon/file-RPC lifecycle. ABI/JS/spec/config and
loaded-module proof are explicit reviewed inputs, never guessed by this module.
"""
import json
import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

GRANARY_PROFILE='granary-decision-v1'
GRANARY_FUNCTIONS={
    'GetBestBuilding':(0x3e4710,'44884c242044884424184889542410555641554157488d6c24f84881ec080100'),
    'QueueNextBuild':(0x3e8190,'40554157488d6c24b14881ecf8000000488b81900000004c8bf98b88d8000000'),
}

INDUSTRIAL_PROFILE = 'industrial-zone-decision-v1'
INDUSTRIAL_FUNCTIONS = {
    'CalculateDistrictValues': (0x3dfee0, '4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'),
    'GetBestBuilding': GRANARY_FUNCTIONS['GetBestBuilding'],
    'QueueNextBuild': GRANARY_FUNCTIONS['QueueNextBuild'],
    'BuildBuilding': (0x3df040, '48895c241048896c2418565741564881ec80000000488bd9498bf1488b899000'),
}


def validate_industrial_config(config):
    if config.get('profile') != INDUSTRIAL_PROFILE or config.get('mappingVerified') is not True:
        raise ValueError('Explicit reviewed IZ mapping required')
    for key, low, high in [('buildingIndexLimit', 1, 4096)]:
        if type(config.get(key)) is not int or not low <= config[key] <= high:
            raise ValueError('Invalid IZ scope/index bound: ' + key)
    targets = config.get('targets')
    if not isinstance(targets, list) or not 1 <= len(targets) <= 2:
        raise ValueError('One or two declared IZ targets required')
    seen = set()
    for target in targets:
        if (not isinstance(target, dict) or type(target.get('player')) is not int
                or not 1 <= target['player'] <= 61 or type(target.get('city')) is not int
                or not 0 <= target['city'] <= 2147483647):
            raise ValueError('Invalid IZ target')
        key = (target['player'], target['city'])
        if key in seen:
            raise ValueError('Duplicate IZ target')
        seen.add(key)
    for key in ['workshopIndex', 'factoryIndex']:
        if type(config.get(key)) is not int or not 0 <= config[key] < config['buildingIndexLimit']:
            raise ValueError('Invalid IZ mapped index: ' + key)
    if (config['workshopIndex'] == config['factoryIndex'] or config.get('workshopType') != 'BUILDING_WORKSHOP'
            or config.get('factoryType') != 'BUILDING_FACTORY'):
        raise ValueError('Wrong IZ building identities')
    for key, value in dict(maxPairs=64, maxCallbacks=10000, maxRows=64, maxThreads=8, maxScopeDepth=16).items():
        if type(config.get(key)) is not int or config[key] != value:
            raise ValueError('Unreviewed IZ bound: ' + key)


def _validate_industrial_contract(spec, config, expected_hooks):
    validate_industrial_config(config)
    rows = spec.get('functions')
    if type(expected_hooks) is not int or expected_hooks != 4 or not isinstance(rows, list) or len(rows) != 4:
        raise ValueError('Wrong exact IZ hook count')
    if any(not isinstance(f, dict) or type(f.get('rva')) is not int
           or not isinstance(f.get('name'), str) or not isinstance(f.get('bytes'), str) for f in rows):
        raise ValueError('Malformed IZ boundary')
    if len({f['name'] for f in rows}) != 4 or {f['name']: (f['rva'], f['bytes']) for f in rows} != INDUSTRIAL_FUNCTIONS:
        raise ValueError('Unreviewed IZ boundary/fingerprint')
    if (spec.get('sha256') != '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
            or spec.get('timestamp') != 1719431003 or spec.get('image_size') != 12976128
            or not isinstance(spec.get('path'), str) or not spec['path']):
        raise ValueError('Unreviewed IZ native build')


def _validate_industrial_status(status, spec, *, enabled, config):
    if config is None or config.get('profile') != INDUSTRIAL_PROFILE:
        raise ValueError('IZ status requires explicit configuration')
    _validate_industrial_contract(spec, config, 4)
    if not (status.get('installed') is True and type(status.get('hooks')) is int and status['hooks'] == 4
            and status.get('enabled') is enabled and isinstance(status.get('module_path'), str)
            and status['module_path'].lower() == spec['path'].lower() and status.get('module_size') == spec['image_size']
            and status.get('loaded_timestamp') == spec['timestamp'] and status.get('validated_entry_fingerprints') == spec['functions']
            and status.get('config') == config and status.get('read_only') is True):
        raise ValueError('IZ install/module/config proof mismatch')


def _validate_industrial_snapshot(snapshot, *, config):
    if config is None or config.get('profile') != INDUSTRIAL_PROFILE or snapshot.get('profile') != INDUSTRIAL_PROFILE:
        raise ValueError('IZ snapshot/config mismatch')
    validate_industrial_config(config)
    stats, rows, pending = snapshot.get('stats'), snapshot.get('records'), snapshot.get('pendingPairs')
    if snapshot.get('read_only') is not True or snapshot.get('paired') is not True or not isinstance(stats, dict):
        raise ValueError('Unknown IZ payload contract')
    for key in ['callbacks', 'completedPairs', 'errors', 'identityChanges', 'budgetSuppressed']:
        if type(stats.get(key)) is not int or stats[key] < 0:
            raise ValueError('Malformed IZ counter: ' + key)
    if (not isinstance(rows, list) or len(rows) != stats['completedPairs'] or len(rows) > 64
            or any(not isinstance(r, dict) or r.get('kind') not in INDUSTRIAL_FUNCTIONS for r in rows)
            or type(pending) is not int or not 0 <= pending <= 64 or len(rows) + pending > 64):
        raise ValueError('IZ pair/scope budget violated')
    frozen = snapshot.get('frozenPendingPairs')
    if frozen is not None and (type(frozen) is not int or not 0 <= frozen <= 64):
        raise ValueError('IZ frozen pending scope budget violated')
    if stats['callbacks'] >= config['maxCallbacks'] and (snapshot.get('enabled') is not False or snapshot.get('saturated') is not True):
        raise ValueError('IZ callback budget did not stop observation')
    targets = {(target['player'], target['city']) for target in config['targets']}
    for row in rows:
        identity = row.get('entry', {}).get('identity', {})
        if (identity.get('owner'), identity.get('city')) not in targets:
            raise ValueError('IZ record scope mismatch')
    return bool(snapshot.get('saturated') or stats['completedPairs'] >= config['maxPairs'])


def write(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');tmp.replace(path)


def _validate_legacy_contract(spec,config,expected_hooks):
    if expected_hooks!=2 or len(spec['functions'])!=2:
        raise ValueError('This observer permits exactly two reviewed boundaries')
    if len({f['name']for f in spec['functions']})!=2:
        raise ValueError('Duplicate observer boundary')
    for f in spec['functions']:
        if not isinstance(f['rva'],int)or f['rva']<0 or not re.fullmatch(r'[0-9a-fA-F]{64}',f['bytes']):
            raise ValueError('Missing exact32-byte entry fingerprint')
    profile=config.get('profile')
    if profile is None:
        if config.get('player')!=3 or config.get('city')!=655369 or config.get('maxPairs')!=64:
            raise ValueError('Wrong bounded material-observer scope')
    elif profile==GRANARY_PROFILE:
        if not(config.get('player')==3 and config.get('city')==196610
               and config.get('buildingIndex')==3 and config.get('buildingType')=='BUILDING_GRANARY'
               and config.get('maxPairs')==64 and config.get('mappingVerified')is True
               and type(config.get('buildingIndexLimit'))is int and 3<config['buildingIndexLimit']<=4096):
            raise ValueError('Wrong reviewed Granary scope/mapping')
        actual={f['name']:(f['rva'],f['bytes'])for f in spec['functions']}
        if actual!=GRANARY_FUNCTIONS:
            raise ValueError('Unreviewed Granary boundaries/fingerprints')
        if not(spec.get('sha256')=='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
               and spec.get('timestamp')==1719431003 and spec.get('image_size')==12976128):
            raise ValueError('Unreviewed Granary native build')
    else:
        raise ValueError('Unknown observer profile')


def _validate_legacy_status(status,spec,*,enabled,config=None):
    if not(status.get('installed')and status.get('hooks')==2 and status.get('enabled')is enabled
           and status.get('module_path','').lower()==spec['path'].lower()
           and status.get('module_size')==spec['image_size']
           and status.get('loaded_timestamp')==spec['timestamp']
           and status.get('validated_entry_fingerprints')==spec['functions']):
        raise ValueError('Observer installation/enable/module proof mismatch')
    decision={f['name']for f in spec['functions']}==set(GRANARY_FUNCTIONS)
    if config is not None:
        validate_contract(spec,config,2)
    if decision:
        if config is None or config.get('profile')!=GRANARY_PROFILE:
            raise ValueError('Granary status requires explicit configuration')
        if status.get('config')!=config or status.get('read_only')is not True:
            raise ValueError('Granary status/config/read-only mismatch')


def _validate_legacy_snapshot(snapshot,*,config=None):
    stats=snapshot['stats']
    if snapshot.get('read_only')is not True or snapshot.get('paired')is not True:
        raise ValueError('Unknown observer payload contract')
    if not isinstance(stats.get('completedPairs'),int)or not 0<=stats['completedPairs']<=64:
        raise ValueError('Observer pair budget violated')
    if snapshot.get('profile')not in(None,GRANARY_PROFILE):
        raise ValueError('Unknown snapshot profile')
    if config is not None and config.get('profile')not in(None,GRANARY_PROFILE):
        raise ValueError('Unknown observer profile')
    if snapshot.get('profile')==GRANARY_PROFILE or(config is not None and config.get('profile')==GRANARY_PROFILE):
        if config is None or config.get('profile')!=GRANARY_PROFILE or snapshot.get('profile')!=GRANARY_PROFILE:
            raise ValueError('Granary snapshot/config profile mismatch')
        records=snapshot.get('records');pending=snapshot.get('pendingPairs')
        if type(stats['completedPairs'])is not int:
            raise ValueError('Granary completed pair count is not an integer')
        if not isinstance(records,list)or len(records)!=stats['completedPairs']:
            raise ValueError('Granary paired record count mismatch')
        if type(pending)is not int or pending<0 or stats['completedPairs']+pending>64:
            raise ValueError('Granary pending pair budget violated')
        if any(not isinstance(row,dict)or row.get('kind')not in GRANARY_FUNCTIONS for row in records):
            raise ValueError('Unknown Granary record boundary')
    return bool(snapshot.get('saturated')or stats['completedPairs']>=64)


def prove_loaded_module(owner,spec,output):
    if owner.poll() is not None:raise RuntimeError('Exact native exited before module query')
    code="Get-Process -Id "+str(int(owner.identity['pid']))+" -ErrorAction Stop | ForEach-Object { $_.Modules } | Where-Object { $_.ModuleName -match '^GameCore_XP2' } | Select-Object ModuleName,FileName,@{Name='base';Expression={$_.BaseAddress.ToInt64()}},@{Name='size';Expression={$_.ModuleMemorySize}} | ConvertTo-Json -Compress"
    raw=subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=json.loads(raw)if raw.strip()else[]
    if isinstance(rows,dict):rows=[rows]
    if any('GameCore_XP2_CE'in row['ModuleName']for row in rows):raise RuntimeError('CE proxy module loaded')
    matches=[row for row in rows if row['FileName'].lower()==spec['path'].lower()]
    if len(matches)!=1 or matches[0]['size']!=spec['image_size']:raise RuntimeError('Loaded native module path/size mismatch')
    digest=hashlib.sha256(Path(spec['path']).read_bytes()).hexdigest()
    if digest!=spec['sha256']or owner.poll() is not None:raise RuntimeError('Native module hash/owner changed')
    proof={'verified':True,'identity':owner.identity,'module':matches[0],'sha256':digest,'other_XP2_modules':rows}
    write(output,proof);return proof


class NativeObserver:
    """One attach/start; freeze before Menu; retain until exact native exit."""
    def __init__(self,output,owner,*,script,spec,config,dependencies,loaded_module,python=None):
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=False)
        self.owner=owner;self.spec=json.loads(Path(spec).read_text());self.config=json.loads(Path(config).read_text())
        validate_contract(self.spec,self.config,expected_hook_count(self.config))
        if owner.poll()is not None:raise RuntimeError('Native owner already exited')
        proof=json.loads(Path(loaded_module).read_text())
        if proof.get('identity')!=owner.identity or not proof.get('verified'):
            raise ValueError('External loaded-module proof does not match held owner')
        for name,path in [('trace.js',script),('native-spec.json',spec),('observer-config.json',config),('loaded-module.json',loaded_module)]:
            (self.output/name).write_bytes(Path(path).read_bytes())
        write(self.output/'native-owner.json',owner.identity)
        self.dependencies=Path(dependencies).resolve();self.process=None;self.seq=0;self.frozen=False
        self.python=Path(python or sys._base_executable)

    def _intent(self,name,text):
        with (self.output/name).open('x',encoding='utf-8')as stream:
            stream.write(text);stream.flush();os.fsync(stream.fileno())

    def _wait(self,name,seconds=20,*,check_errors=True):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            path=self.output/name
            if path.exists():return json.loads(path.read_text())
            if self.owner.poll()is not None:raise RuntimeError('Held native exited before observer acknowledgement')
            if check_errors and (self.output/'trace-daemon-error.json').exists():
                raise RuntimeError('Observer error; preserve retained daemon/native')
            if self.process is not None and self.process.poll()is not None:
                raise RuntimeError('Observer process exited before native')
            time.sleep(.1)
        raise TimeoutError('Unconfirmed observer action; no replay: '+name)

    def attach_disabled(self):
        if self.process is not None:raise RuntimeError('Observer attach cannot repeat')
        log=(self.output/'trace-daemon.log').open('xb')
        try:
            self.process=subprocess.Popen([str(self.python),'-B',str(Path(__file__).with_name('observer_daemon.py')),
                '--output',str(self.output),'--dependencies',str(self.dependencies)],stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
        finally:log.close()
        ready=self._wait('trace-ready.json');validate_status(ready['status'],self.spec,enabled=False,config=self.config)
        return ready

    def start(self):
        self._intent('trace-start.request','once')
        result=self._wait('trace-started.json');validate_status(result['status'],self.spec,enabled=True,config=self.config)
        return result

    def snapshot(self,label):
        if not re.fullmatch(r'[A-Za-z0-9_-]+',label):raise ValueError('Invalid snapshot label')
        if self.frozen:raise RuntimeError('Observer is frozen')
        self.seq+=1;token=str(self.seq).zfill(3)+'-'+label
        self._intent('snapshot-intent-'+token+'.json',json.dumps({'token':token,'read_only':True}))
        self._intent('trace-snapshot.request',token)
        result=self._wait('trace-snapshot-'+token+'.json')
        saturated=validate_snapshot(result,config=self.config)
        if result['stats'].get('errors',0)or result['stats'].get('identityChanges',0):
            raise RuntimeError('Observer read/identity errors; stop at inactive boundary')
        return result,saturated

    def before_menu(self):
        # Even after a scientific observer error, request a verified inert freeze
        # if the daemon still processes RPC. Never unload/detach a live target.
        if self.frozen:return
        self._intent('trace-freeze.request','cleanup-once')
        result=self._wait('trace-counts.json',check_errors=False)
        config=getattr(self,'config',None) # Legacy offline lifecycle adapters omit it.
        validate_status(result['status'],self.spec,enabled=False,config=config)
        validate_snapshot(result['snapshot'],config=config)
        if result['snapshot'].get('frozenPendingPairs',0)!=0:
            raise RuntimeError('Observer freeze retained unfinished pairs')
        self.frozen=True

    def after_native_exit(self):
        if self.owner.poll()is None:raise RuntimeError('Native still alive; observer must remain retained')
        if self.process is None:raise RuntimeError('Observer was not attached')
        self.process.wait(timeout=20)
        value=json.loads((self.output/'trace-daemon-exit.json').read_text())
        if value.get('identity')!=self.owner.identity or not value.get('native_absent')or value.get('explicit_detach'):
            raise RuntimeError('Observer exit/retention proof failed')
        if self.process.returncode!=0:raise RuntimeError('Observer process exited nonzero')
        return value


# Explicit placement profile: the two historical profiles still use their exact
# original validation. Extra hooks are accepted only with this fixed build/site
# set and bounded target, not as a generic relaxation of the observer boundary.
PLACEMENT_PROFILE = 'quarter-placement-v1'
PLACEMENT_FUNCTIONS = {'district_value': (5428480, '44894c24204c894424188954241048894c240855415441554157488dac2458fe'), 'net_value': (5416000, '8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'), 'normalize': (5419280, '48895c240848896c24104889742420574883ec30418bf0498be9488bfa488bd9'), 'normalize_bonus': (5419451, '8b08b8000900003bc80f4fc848630781c1000100004863c9480fafc848c1f908'), 'competitor_compare': (5430715, '3b107e14488b4580f680e00000000475072bf24889742460488b5580f3440f10'), 'competitor_merge': (5430739, '488b5580f3440f100d983d49000f29b42470020000807a58000f841901000066'), 'city_evaluation': (4074144, '48894c240855574154488dac2470ffffff4881ec90010000817964f1d8ffff4c'), 'get_best_district': (4082256, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'), 'try_reserve': (4104256, '48895c240848896c2410488974241848897c242041564883ec20498bf1418bf8')}

PLACEMENT_POST_PROFILE = 'quarter-placement-post-v2'
PLACEMENT_POST_FUNCTIONS = {'district_value': (5428480, '44894c24204c894424188954241048894c240855415441554157488dac2458fe'), 'net_value': (5416000, '8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'), 'competitor_compare': (5430715, '3b107e14488b4580f680e00000000475072bf24889742460488b5580f3440f10'), 'competitor_merge': (5430739, '488b5580f3440f100d983d49000f29b42470020000807a58000f841901000066'), 'city_evaluation': (4074144, '48894c240855574154488dac2470ffffff4881ec90010000817964f1d8ffff4c'), 'get_best_district': (4082256, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'), 'try_reserve': (4104256, '48895c240848896c2410488974241848897c242041564883ec20498bf1418bf8'), 'wrapper_normalize_post': (5429533, '0338488b458048897c2460488b9808010000488bb800010000483bfb0f84ab00'), 'own_normalize_post': (5429708, '8b08010e488b75b84883c708483bfb0f856fffffff448b6424504c8b6db04d85'), 'competing_normalize_post': (5430507, '41ffc58b0841010c244c8b6590453bee730733c9e97cffffff488b5de04883c7')}


def expected_hook_count(config):
    if config.get('profile') == INDUSTRIAL_PROFILE:
        return 4
    if config.get('profile') == PLACEMENT_POST_PROFILE:
        return 10
    return 9 if config.get('profile') == PLACEMENT_PROFILE else 2


def validate_placement_config(config):
    if config.get('profile') not in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE):
        raise ValueError('Unknown named placement profile')
    fixed = {
        'profile': config.get('profile'), 'player': 3, 'city': 131073,
        'districtType': 'DISTRICT_CSC_BAKERS_QUARTER', 'mappingVerified': True,
        'mapWidth': 74, 'mapHeight': 46, 'maxPairs': 64, 'maxChoices': 32,
        'maxRows': 64, 'maxScopeDepth': 16, 'maxThreads': 8,
        'maxNormalizations': 512, 'maxValuesPerNet': 4,
        'maxCallbacks': 1000000, 'maxTrackedMs': 300000,
    }
    if config.get('profile') == PLACEMENT_POST_PROFILE:
        fixed['privateYieldDefaultValue'] = 1
    for key, value in fixed.items():
        if type(config.get(key)) is not type(value) or config[key] != value:
            raise ValueError('Unreviewed placement configuration: ' + key)
    for index, limit, maximum in [('districtIndex', 'districtIndexLimit', 4096),
                                  ('privateYieldIndex', 'yieldIndexLimit', 64)]:
        if (type(config.get(index)) is not int or type(config.get(limit)) is not int
                or not 0 <= config[index] < config[limit] <= maximum):
            raise ValueError('Invalid native placement mapping: ' + index)

    if config.get('profile') == PLACEMENT_POST_PROFILE:
        definition = config.get('yieldDefinitions', {}).get(str(config.get('privateYieldIndex')))
        if (not isinstance(definition, dict) or definition.get('DefaultValue') != 1
                or definition.get('type') != 'YIELD_CSC_AI_PLACEMENT'):
            raise ValueError('Native private DefaultValue1 is required for conditional inference')


def validate_contract(spec, config, expected_hooks):
    if config.get('profile') == INDUSTRIAL_PROFILE:
        return _validate_industrial_contract(spec, config, expected_hooks)
    if config.get('profile') not in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE):
        return _validate_legacy_contract(spec, config, expected_hooks)
    validate_placement_config(config)
    functions = PLACEMENT_POST_FUNCTIONS if config.get('profile') == PLACEMENT_POST_PROFILE else PLACEMENT_FUNCTIONS
    count = expected_hook_count(config)
    if type(expected_hooks) is not int or expected_hooks != count:
        raise ValueError('Wrong exact named placement boundary count')
    rows = spec.get('functions')
    if not isinstance(rows, list) or len(rows) != count:
        raise ValueError('Wrong placement boundary count')
    if any(not isinstance(f, dict) or type(f.get('rva')) is not int
           or not isinstance(f.get('name'), str) or not isinstance(f.get('bytes'), str)
           for f in rows):
        raise ValueError('Malformed placement boundary')
    if len({f['name'] for f in rows}) != count:
        raise ValueError('Duplicate placement boundary')
    actual = {f['name']: (f['rva'], f['bytes']) for f in rows}
    if actual != functions:
        raise ValueError('Unreviewed placement boundary/fingerprint')
    if (spec.get('sha256') != '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
            or spec.get('timestamp') != 1719431003 or spec.get('image_size') != 12976128
            or not isinstance(spec.get('path'), str) or not spec['path']):
        raise ValueError('Unreviewed placement native build')


def validate_status(status, spec, *, enabled, config=None):
    if ({f.get('name') for f in spec.get('functions', [])} == set(INDUSTRIAL_FUNCTIONS)
            or (config is not None and config.get('profile') == INDUSTRIAL_PROFILE)):
        return _validate_industrial_status(status, spec, enabled=enabled, config=config)
    placement = ({f.get('name') for f in spec.get('functions', [])}
                 in (set(PLACEMENT_FUNCTIONS), set(PLACEMENT_POST_FUNCTIONS)))
    if not placement and (config is None or config.get('profile') not in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE)):
        return _validate_legacy_status(status, spec, enabled=enabled, config=config)
    if config is None or config.get('profile') not in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE):
        raise ValueError('Placement status requires explicit configuration')
    validate_contract(spec, config, expected_hook_count(config))
    if not (status.get('installed') is True and type(status.get('hooks')) is int
            and status['hooks'] == expected_hook_count(config) and status.get('enabled') is enabled
            and isinstance(status.get('module_path'), str)
            and status['module_path'].lower() == spec['path'].lower()
            and status.get('module_size') == spec['image_size']
            and status.get('loaded_timestamp') == spec['timestamp']
            and status.get('validated_entry_fingerprints') == spec['functions']
            and status.get('config') == config and status.get('read_only') is True):
        raise ValueError('Placement install/module/config proof mismatch')


def validate_snapshot(snapshot, *, config=None):
    if snapshot.get('profile') == INDUSTRIAL_PROFILE or (config is not None and config.get('profile') == INDUSTRIAL_PROFILE):
        return _validate_industrial_snapshot(snapshot, config=config)
    placement = snapshot.get('profile') in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE)
    if not placement and (config is None or config.get('profile') not in (PLACEMENT_PROFILE, PLACEMENT_POST_PROFILE)):
        return _validate_legacy_snapshot(snapshot, config=config)
    if not placement or config is None or config.get('profile') != snapshot.get('profile'):
        raise ValueError('Placement snapshot/config mismatch')
    validate_placement_config(config)
    stats = snapshot.get('stats')
    if (not isinstance(stats, dict) or snapshot.get('read_only') is not True
            or snapshot.get('paired') is not True):
        raise ValueError('Unknown placement payload contract')
    for key in ['callbacks', 'completedPairs', 'completedCandidatesTotal', 'errors',
                'identityChanges', 'revisionsNotRetained', 'dropped', 'elapsedTrackedMs']:
        if type(stats.get(key)) is not int or stats[key] < 0:
            raise ValueError('Malformed placement counter: ' + key)
    for key, cap in [('candidates', 64), ('evaluations', 64), ('choices', 32), ('reservations', 32)]:
        rows = snapshot.get(key)
        if not isinstance(rows, list) or len(rows) > cap or any(not isinstance(r, dict) for r in rows):
            raise ValueError('Placement collection budget/type violation: ' + key)
    if len(snapshot['candidates']) != stats['completedPairs']:
        raise ValueError('Placement candidate count mismatch')
    pending = snapshot.get('pendingPairs')
    if type(pending) is not int or not 0 <= pending <= 8*16:
        raise ValueError('Placement pending scope budget violated')
    frozen = snapshot.get('frozenPendingPairs')
    if frozen is not None and (type(frozen) is not int or not 0 <= frozen <= 8*16):
        raise ValueError('Placement frozen pending budget violated')
    for row in snapshot['candidates']:
        if row.get('kind') != 'net_value' or row.get('districtIndex') != config['districtIndex']:
            raise ValueError('Unreviewed placement candidate')
        nested = row.get('districtValues')
        if not isinstance(nested, list) or len(nested) > 4:
            raise ValueError('Placement nested value budget violated')
        for value in nested:
            normalizations = value.get('normalizations')
            if not isinstance(normalizations, list) or len(normalizations) > 512:
                raise ValueError('Placement normalization budget violated')
            if config.get('profile') == PLACEMENT_POST_PROFILE:
                for norm in normalizations:
                    if norm.get('effectiveBonusQ8') is not None:
                        raise ValueError('Post-call profile cannot directly observe effective bonus')
                    if norm.get('group') != 'wrapper' and (norm.get('rawInteger') is not None or norm.get('rawInputQ8') is not None):
                        raise ValueError('Own/competing raw input is unobserved at post sites')
    return bool(snapshot.get('saturated'))
