"""Shared native-session infrastructure, promoted independently of retired AI tuning.

Launch, CSC-only content selection, exact preference restoration and provenance.
No placement heuristics, private yields, subsidies or game orders. No native I/O
on import. Promoted functions retain the previously exercised source contracts.
"""
import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
from .windows_process import HeldProcess,native_inventory
CSC='c5e66bd1-d804-443b-ac3d-1917a20dba3c'


def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');tmp.replace(p)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def parse(raw,marker):return json.loads(re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)[-1])

def flags(r,label):
 raw=r.cmd("local a={};for _,m in ipairs(Modding.GetInstalledMods())do if m.Source=='Mod'and not m.Official then a[m.Id]=a[m.Id]or m.Enabled;print('CSC_PROFILE_ENTRY',m.Id,tostring(m.SubscriptionId or ''),tostring(m.SourceFileName or ''),tostring(m.Enabled))end end;local entries={};for k,v in pairs(a)do entries[#entries+1]='\"'..k..'\":'..tostring(v)end;print('CSC_PROFILE_PREFS={'..table.concat(entries,',')..'}');print('CSC_PROFILE_AUTO',Automation.IsAutoStartEnabled());",'MainMenu',label)
 rows=[dict(id=i,subscription=sub,file=file,enabled=enabled=='true')for i,sub,file,enabled in re.findall(r'CSC_PROFILE_ENTRY\s+([^\s]+)\t([^\t\r\n]*)\t([^\t\r\n]*)\t(true|false)',raw)]
 return dict(mods=parse(raw,'CSC_PROFILE_PREFS'),auto_start=re.search(r'CSC_PROFILE_AUTO\s+(true|false)',raw)[1]=='true',entries=sorted(rows,key=lambda v:(v['id'],v['subscription'],v['file'])))

def restore_preferences(r,out):
 original=read(out/'original-preferences.json')
 entries=','.join('['+json.dumps(v['id']+'|'+v['subscription']+'|'+v['file'])+']='+str(v['enabled']).lower()for v in original['entries'])
 code='local wanted={'+entries+"};local function key(m)return m.Id..'|'..tostring(m.SubscriptionId or '')..'|'..tostring(m.SourceFileName or '')end;local disable={};for _,m in ipairs(Modding.GetInstalledMods())do if wanted[key(m)]==false and m.Enabled then disable[#disable+1]=m.Handle end end;if #disable>0 then Modding.DisableMod(disable)end;for _,m in ipairs(Modding.GetInstalledMods())do if wanted[key(m)]==true and not m.Enabled then Modding.EnableMod(m.Handle,true)end end;Automation.SetAutoStartEnabled("+str(original['auto_start']).lower()+');'
 r.cmd(code,'MainMenu','restore-exact-subscription-preferences');r.wait('MainMenu',90)
 actual=flags(r,'verify-exact-subscription-preferences');assert actual==original
 write(out/'preferences-restored.json',dict(verified=True,mods=len(actual['mods']),installed_entries=len(actual['entries']),auto_start=actual['auto_start']))

def launch(a, out):
    """One direct launch; allow only the reviewed exit53→fresh Steam successor."""
    directory = out/'sdk-working'
    directory.mkdir()
    (directory/'steam_appid.txt').write_text('289070\n', encoding='ascii')
    before = time.time()
    process = subprocess.Popen([str(a.binary)], cwd=directory, creationflags=subprocess.CREATE_NO_WINDOW)
    write_json(out/'launch-bootstrap.json',dict(pid=process.pid,binary=str(a.binary),time=before))
    time.sleep(2)
    if process.poll() is None:
        return HeldProcess.from_popen(process)
    write_json(out/'launch-bootstrap-exit.json',dict(pid=process.pid,exit_code=process.returncode))
    if process.returncode != 53:
        raise RuntimeError('Direct native bootstrap exited; no automatic relaunch')
    deadline = time.monotonic()+20
    while time.monotonic()<deadline:
        rows=native_inventory()
        if rows: break
        time.sleep(.5)
    if len(rows)!=1:
        raise RuntimeError('Steam successor missing or ambiguous; preserve owners')
    row=rows[0];identity=row['identity']
    if Path(identity['executable_path']).resolve()!=a.binary.resolve():
        raise RuntimeError('Unexpected Steam successor executable')
    created=identity['creation_filetime']/10_000_000-11644473600
    if not before-1<=created<=time.time():
        raise RuntimeError('Steam successor predates this launch')
    code="Get-Process -Id "+str(int(row['ParentProcessId']))+" -ErrorAction Stop | Select-Object ProcessName,Path | ConvertTo-Json -Compress"
    parent=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
    if parent['ProcessName'].lower()!='steam':
        raise RuntimeError('Successor is not Steam-owned')
    held=HeldProcess(row['pid'])
    if held.identity!=identity:
        raise RuntimeError('Steam successor identity changed before hold')
    write_json(out/'launch-steam-successor.json',dict(identity=identity,parent=parent,bootstrap_exit=53))
    return held

def archive_sources(pins, directory):
    """Archive code and small metadata; immutable heavy inputs stay hash/path."""
    allowed = {'.py', '.lua', '.sql', '.xml', '.json', '.md', '.js', '.c'}
    archived, referenced = [], []
    directory.mkdir()
    for i, path in enumerate(pins):
        source = Path(path)
        if source.suffix.lower() in allowed and source.stat().st_size <= 1024 * 1024:
            destination = directory / (str(i).zfill(3) + '-' + source.name)
            shutil.copy2(source, destination)
            archived.append(dict(source=path, archive=str(destination), bytes=source.stat().st_size))
        else:
            referenced.append(dict(path=path, sha256=pins[path], bytes=source.stat().st_size))
    return dict(policy='Executed text and metadata <=1MiB only; no game/save/DLL/EXE/assets/package clone',
                archived=archived, hash_path_only=referenced)

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

write_json=write


def configure(r, out, profile='BASIC'):
    """Select CSC plus official content; restore the exact entries after testing."""
    if profile != 'BASIC': raise ValueError('Clean bridge trials use CSC-only content')
    original = flags(r, 'save-menu-before-configuration')
    if (out/'original-preferences.json').exists(): raise RuntimeError('No configuration replay')
    write(out/'original-preferences.json', original)
    code = "local a={};for _,m in ipairs(Modding.GetInstalledMods())do if m.Source=='Mod'and not m.Official and m.Enabled and m.Id~='"+CSC+"'then a[#a+1]=m.Handle end end;if #a>0 then Modding.DisableMod(a)end;"
    try: r.cmd(code, 'MainMenu', 'disable-unrelated-mods-once')
    except RuntimeError as error: write(out/'disable-ack-warning.json', dict(error=str(error), no_resend=True))
    r.wait('MainMenu', 90)
    selected = flags(r, 'check-CSC-before-enable')
    if not selected['mods'].get(CSC):
        code = "local best=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"+CSC+"'then assert(not best,'Ambiguous CSC entry');best=m end end;assert(best,'CSC missing');Modding.EnableMod(best.Handle,true);"
        try: r.cmd(code, 'MainMenu', 'enable-CSC-once')
        except RuntimeError as error: write(out/'enable-ack-warning.json', dict(error=str(error), no_resend=True))
        r.wait('MainMenu',90)
    selected = flags(r,'verify-CSC-only')
    if not selected['mods'].get(CSC) or any(v for k,v in selected['mods'].items() if k!=CSC):
        raise RuntimeError('CSC-only preference selection not verified')
    write(out/'native-menu-configuration.json',dict(verified=True,profile='native-bridge-clean',enabled_mod_ids=[CSC],legacy_tuning=False,assistance=False,subsidies=False))
