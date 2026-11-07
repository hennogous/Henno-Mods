"""Supported, one-shot exact-boundary save; no load/restart policy on import."""
from pathlib import Path
import hashlib,json,re,shutil,time
from .transport import MissingAcknowledgment


def archive_autosave_window(native_directory, archive_directory, first, last, after_ns):
    """Preserve existing autosaves after a finite play window without a new game command.

    The receipt proves file provenance. A cold load still has to verify the
    game clock and scenario before either arm can use the save.
    """
    archive_directory.mkdir(parents=True, exist_ok=True)
    receipts = []
    for turn in range(first, last + 1):
        source = Path(native_directory) / 'auto' / f'AutoSave_{turn:04d}.Civ6Save'
        row = dict(turn=turn, source=str(source))
        try:
            original = source.stat()
            if original.st_mtime_ns < after_ns:
                receipts.append(dict(row, status='predates-window'))
                continue
            data = source.read_bytes()
            current = source.stat()
        except FileNotFoundError:
            receipts.append(dict(row, status='unavailable'))
            continue
        if (len(data), current.st_mtime_ns, current.st_size) != (
                original.st_size, original.st_mtime_ns, original.st_size) or not data.startswith(b'CIV6'):
            receipts.append(dict(row, status='unsettled'))
            continue
        archive = archive_directory / f'source-{turn:03d}.Civ6Save'
        with archive.open('xb') as stream:
            stream.write(data)
        receipts.append(dict(row, status='archived', archive=str(archive), size=len(data),
                             sha256=hashlib.sha256(data).hexdigest(), modified_ns=original.st_mtime_ns))
    return receipts


def checkpoint_name(name,archive):
    """Stable name per archived boundary; another run's save is never reused."""
    assert re.fullmatch(r'[A-Za-z0-9_-]{1,96}',name),'Safe unique save name required'
    identity=hashlib.sha256(str(Path(archive).resolve()).casefold().encode('utf-8')).hexdigest()[:12]
    return name[:83]+'_'+identity


def validate_ui_save_phase(core,ui):
    """UI can remain one turn behind an inactive Core; Core owns the save clock.

    This permits no turn advance, role switch or retry. Both contexts must be
    inactive and human-controlled; future or older UI phases remain invalid.
    """
    assert not core['active'] and core['local_player']==0 and core['player0_human']
    assert not ui['active'] and ui['local_player']==0 and ui['player0_human'] and ui['player0_alive']
    assert ui['turn'] in (core['turn'],core['turn']-1),'UI clock outside the observed single-turn lag'
    return core['turn']-ui['turn']


def save_inactive_boundary(r,*,turn,name,native_directory,archive,timeout=60):
    assert re.fullmatch(r'[A-Za-z0-9_-]{1,96}',name),'Safe unique save name required'
    requested_name=name;archive=Path(archive);name=checkpoint_name(name,archive)
    native=Path(native_directory)/(name+'.Civ6Save')
    assert not native.exists()and not archive.exists(),'Never overwrite a checkpoint'
    r.ready(turn,'before-exact-checkpoint')
    proof=r.state_read('exact-checkpoint-before')
    assert proof['turn']==turn and not proof['active']and proof['local_player']==0 and proof['player0_human']
    raw=r.cmd("local p=Players[0];print('CSC_EXACT_CHECKPOINT_UI',Game.GetCurrentGameTurn(),AutoplayManager.IsActive(),Game.GetLocalPlayer(),p and p:IsHuman(),p and p:IsAlive())",'PlotInfo','checkpoint-ui-phase')
    t,a,p,h,alive=re.findall(r'CSC_EXACT_CHECKPOINT_UI\s+(\d+)\s+(true|false)\s+(-?\d+)\s+(true|false)\s+(true|false)',raw)[-1]
    ui=dict(turn=int(t),active=a=='true',local_player=int(p),player0_human=h=='true',player0_alive=alive=='true')
    ui_lag=validate_ui_save_phase(proof,ui)
    n=json.dumps(name)
    code="""assert(not AutoplayManager.IsActive()and Game.GetLocalPlayer()==0 and(Game.GetCurrentGameTurn()==%d or Game.GetCurrentGameTurn()==%d))
if CSC_EXACT_CHECKPOINT_SAVE and CSC_EXACT_CHECKPOINT_SAVE.handler then Events.SaveComplete.Remove(CSC_EXACT_CHECKPOINT_SAVE.handler)end
CSC_EXACT_CHECKPOINT_SAVE={name=%s,completed=false}
CSC_EXACT_CHECKPOINT_SAVE.handler=function()CSC_EXACT_CHECKPOINT_SAVE.completed=true end
Events.SaveComplete.Add(CSC_EXACT_CHECKPOINT_SAVE.handler)
Network.SaveGame({Name=%s,Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false})
print('CSC_EXACT_CHECKPOINT_REQUESTED',%s)"""%(turn,turn-1,n,n,n)
    acknowledged=True
    try:r.cmd(code,'PlotInfo','save-exact-boundary-'+str(turn))
    except MissingAcknowledgment:acknowledged=False # Inspect the unique file; never repeat SaveGame.
    deadline=time.monotonic()+timeout;last=None;stable=0
    while time.monotonic()<deadline:
        try:
            size=native.stat().st_size
            with native.open('rb') as stream:head=stream.read(4)
            stable=stable+1 if size==last and size>100000 and head==b'CIV6'else 0;last=size
            if stable>=3:break
        except(OSError,PermissionError):stable=0
        time.sleep(.5)
    else:raise TimeoutError('Native checkpoint file did not settle; never resend blindly')
    raw=r.cmd("print('CSC_EXACT_CHECKPOINT_COMPLETE',CSC_EXACT_CHECKPOINT_SAVE.name,CSC_EXACT_CHECKPOINT_SAVE.completed);if CSC_EXACT_CHECKPOINT_SAVE.completed then Events.SaveComplete.Remove(CSC_EXACT_CHECKPOINT_SAVE.handler)end",'PlotInfo','checkpoint-save-complete')
    assert re.search(r'CSC_EXACT_CHECKPOINT_COMPLETE\s+'+re.escape(name)+r'\s+true',raw),'Native SaveComplete event not observed'
    archive.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(native,archive)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    digest=sha(native);assert sha(archive)==digest
    after=r.state_read('exact-checkpoint-after');assert all(proof[k]==after[k]for k in('turn','active','remaining','local_player','player0_human'))
    return {'verified':True,'turn':turn,'requested_name':requested_name,'unique_name':name,'native_save':str(native),'archive':str(archive),'sha256':digest,
            'size':native.stat().st_size,'save_requests':1,'save_complete_event':True,'initial_ack':acknowledged,
            'UI_phase':ui,'UI_clock_lag':ui_lag,'native_phase_unchanged':True,'before':proof,'after':after,'native_pid':r.game_pid,'worlds_created':0}
