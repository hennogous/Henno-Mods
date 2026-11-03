"""Conservative collection of disposable Ghidra MCP clones, never master projects.

Managed clones carry exact process-creation identities. Legacy clones without
leases require a quiet grace period. Process discovery failure always preserves
data. All recursive deletion is scoped/checked in this Python module.
"""
from contextlib import contextmanager
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time
import uuid

LEASE = 'session-lease.json'
UUID = re.compile(r'[0-9a-f]{32}')

def atomic_json(path, value):
    path=Path(path);tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');tmp.replace(path)

def process_identity(pid):
    """Return exact creation identity while alive, None if absent; errors raise."""
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)]
    k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=k.OpenProcess(0x1000|0x100000,False,int(pid))
    if not handle:
        error=ctypes.get_last_error()
        if error in (87,1168):return None
        raise ctypes.WinError(error)
    try:
        state=k.WaitForSingleObject(handle,0)
        if state==0:return None
        if state!=258:raise ctypes.WinError(ctypes.get_last_error())
        times=[wintypes.FILETIME()for _ in range(4)]
        if not k.GetProcessTimes(handle,*[ctypes.byref(t)for t in times]):raise ctypes.WinError(ctypes.get_last_error())
        return dict(pid=int(pid),created=(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime)
    finally:k.CloseHandle(handle)

def process_rows():
    script='Get-CimInstance Win32_Process -ErrorAction Stop | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress'
    raw=subprocess.check_output(['powershell','-NoProfile','-Command',script],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=json.loads(raw)
    if not isinstance(rows,list):rows=[rows]
    if not rows:raise RuntimeError('Empty/unverified process inventory')
    return rows

def referenced(root, rows):
    pattern=re.compile(re.escape(str(root).replace('/','\\'))+r'\\([0-9a-f]{32})(?=[\\\s"\x27]|$)',re.I)
    names=set();unscoped_gui=False
    for row in rows:
        command=(row.get('CommandLine')or'').replace('/','\\')
        hits={m.group(1).lower()for m in pattern.finditer(command)};names.update(hits)
        low=command.lower()
        if ('ghidrarun'in low or ('ghidra'in low and '--gui'in low))and not hits:unscoped_gui=True
    return names,unscoped_gui

def is_reparse(path):
    return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

def checked_tree(path, root):
    """Verify exact absolute direct-child scope and every descendant before delete."""
    root=Path(root).absolute();path=Path(path).absolute()
    if root.resolve(strict=True)!=root or is_reparse(root):raise ValueError('Unsafe sessions root')
    if path.parent!=root or not path.is_dir()or not UUID.fullmatch(path.name)or path.resolve(strict=True).parent!=root:
        raise ValueError('Not a direct UUID session child: '+str(path))
    total=0;latest=0.;stack=[path]
    while stack:
        item=stack.pop()
        if is_reparse(item):raise ValueError('Reparse point refused: '+str(item))
        info=item.lstat();latest=max(latest,info.st_mtime,info.st_ctime)
        if stat.S_ISDIR(info.st_mode):stack.extend(item.iterdir())
        elif stat.S_ISREG(info.st_mode):total+=info.st_size
        else:raise ValueError('Unexpected session file type')
    return dict(bytes=total,latest=latest)

def read_lease(path):
    p=Path(path)/LEASE
    if not p.exists():return None
    lease=json.loads(p.read_text(encoding='utf-8'))
    if lease.get('version')!=1 or lease.get('session')!=Path(path).name:raise ValueError('Invalid lease')
    for key in ('owner','worker'):
        ident=lease.get(key)
        if ident is not None and (not isinstance(ident,dict)or type(ident.get('pid'))is not int or ident['pid']<=0
                                  or type(ident.get('created'))is not int or ident['created']<=0):
            raise ValueError('Invalid process lease identity')
    if not lease.get('owner'):raise ValueError('Missing lease owner')
    return lease

def eligible(path, root, rows, *, now=None, grace=600, identity=process_identity, allow_owner=None):
    info=checked_tree(path,root);refs,gui=referenced(Path(root),rows)
    if path.name in refs:return False,'live process references session',info
    if gui:return False,'unscoped Ghidra GUI may own a clone',info
    lease=read_lease(path)
    if lease is None:
        if (time.time()if now is None else now)-info['latest']<grace:return False,'recent unmanaged session',info
    else:
        for key in ('owner','worker'):
            expected=lease.get(key)
            if expected is None:continue
            if key=='owner'and expected==allow_owner:continue
            observed=identity(expected['pid'])
            if observed==expected:return False,'live '+key+' lease',info
    return True,'dead managed lease'if lease else'old unreferenced legacy clone',info

def remove_checked(path,root):
    checked_tree(path,root)  # Revalidate immediately before recursive deletion.
    def readonly_retry(function,name,error):
        if isinstance(error,FileNotFoundError):return
        target=Path(name)
        if not target.is_relative_to(path)or is_reparse(target):raise error
        if not isinstance(error,PermissionError):raise error
        target.chmod(stat.S_IREAD|stat.S_IWRITE);function(name)
    shutil.rmtree(path,onexc=readonly_retry)

@contextmanager
def maintenance_lock(root, identity=None):
    """An OS mutex is released even if a launcher is abruptly terminated."""
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateMutexW.argtypes=[ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR];k.CreateMutexW.restype=wintypes.HANDLE
    k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.WaitForSingleObject.restype=wintypes.DWORD
    k.ReleaseMutex.argtypes=[wintypes.HANDLE];k.CloseHandle.argtypes=[wintypes.HANDLE]
    name='Local\\CSC_GhidraGC_'+hashlib.sha256(str(Path(root).absolute()).lower().encode()).hexdigest()[:24]
    handle=k.CreateMutexW(None,False,name)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    owned=False
    try:
        status=k.WaitForSingleObject(handle,0)
        if status not in (0,128):raise RuntimeError('Another maintenance pass is active')
        owned=True;yield
    finally:
        if owned:k.ReleaseMutex(handle)
        k.CloseHandle(handle)

def collect(root, *, only=None, grace=600, rows_provider=process_rows, identity=process_identity):
    root=Path(root).absolute()
    report=dict(root=str(root),time=time.time(),deleted=[],preserved=[],errors=[],deleted_bytes=0)
    try:
        if root.resolve(strict=True)!=root or is_reparse(root):raise ValueError('Unsafe sessions root')
        with maintenance_lock(root,identity):
            rows=rows_provider()  # Discovery failure aborts before deleting anything.
            candidates=[p for p in root.iterdir()if UUID.fullmatch(p.name)and(only is None or p.name in only)]
            for path in sorted(candidates):
                try:
                    okay,reason,info=eligible(path,root,rows,grace=grace,identity=identity)
                    if not okay:report['preserved'].append(dict(session=path.name,reason=reason));continue
                    # Managed identities are checked once more just before deletion.
                    okay,reason,info=eligible(path,root,rows,grace=grace,identity=identity)
                    if not okay:report['preserved'].append(dict(session=path.name,reason=reason));continue
                    remove_checked(path,root)
                    report['deleted'].append(dict(session=path.name,bytes=info['bytes'],reason=reason))
                    report['deleted_bytes']+=info['bytes']
                except Exception as error:report['errors'].append(dict(session=path.name,error=str(error)))
    except Exception as error:report['errors'].append(dict(error=str(error)))
    return report

def create_session(root):
    root=Path(root).absolute()
    if root.resolve(strict=True)!=root or is_reparse(root):raise ValueError('Unsafe sessions root')
    path=root/uuid.uuid4().hex;path.mkdir()
    atomic_json(path/LEASE,dict(version=1,session=path.name,started=time.time(),owner=process_identity(os.getpid()),worker=None))
    return path

def claim_worker(path,root):
    path=Path(path).absolute();checked_tree(path,root);lease=read_lease(path)
    if not lease or process_identity(lease['owner']['pid'])!=lease['owner']:raise RuntimeError('Worker launcher is no longer alive')
    if lease.get('worker')is not None:raise RuntimeError('Worker already claimed')
    lease['worker']=process_identity(os.getpid());atomic_json(path/LEASE,lease)

def cleanup_owned(path,root):
    """Normal parent cleanup after its child fully exits; no live-worker override."""
    path=Path(path).absolute();me=process_identity(os.getpid());lease=read_lease(path)
    if not lease or lease['owner']!=me:raise RuntimeError('Not this launcher\'s session')
    okay,reason,_=eligible(path,root,process_rows(),allow_owner=me)
    if not okay:raise RuntimeError(reason)
    remove_checked(path,Path(root).absolute())
