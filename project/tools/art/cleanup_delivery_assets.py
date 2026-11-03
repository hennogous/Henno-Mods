"""Consolidate accepted delivery assets without re-exporting animation binaries."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time

from lxml import etree as E
from storage_pivot_trial import ROOT, MOD, POINTS, MODELS, parse, txt, save
from storage_family_pivot import asset

ALIASES = {
    "CSC_TRIAL_BAKERS_Delivery_Split": "CSC_BAKERS_Delivery",
    "CSC_BAKERS_Storage_Delivery_2_Split": "CSC_BAKERS_Delivery",
    "CSC_TAILORS_Storage_Delivery_Split": "CSC_TAILORS_Delivery",
    "CSC_TAILORS_Storage_Delivery_2_Split": "CSC_TAILORS_Delivery",
    "CSC_TRIAL_Delivery_Donkey": "CSC_ALL_Delivery_Donkey",
}
NATIVE = {"CSC_ALL_Delivery_Pivot": "CSC_ALL_Delivery",
          "CSC_TRIAL_Delivery_Donkey": "CSC_ALL_Delivery_Donkey"}
WIN_MOD = Path("C:/Users/Shadow/Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def normalize(root):
    root = copy.deepcopy(root)
    for e in root.iter():
        if e.text is not None and not e.text.strip():
            e.text = None
        e.tail = None
    return E.tostring(root)


def rewrite(root):
    root = copy.deepcopy(root)
    root.find("m_Name").set("text", ALIASES.get(txt(root,"m_Name"),txt(root,"m_Name")))
    for tag, mapping in (("m_EntryName",ALIASES),("m_GeoName",NATIVE),("m_AnimationName",NATIVE)):
        for e in root.findall(".//"+tag):
            e.set("text",mapping.get(e.get("text"),e.get("text")))
    for p in root.findall(POINTS+"/Element"):
        e = p.find("m_Name")
        e.set("text",ALIASES.get(e.get("text"),e.get("text")))
        if e.get("text")=="Donkey_TerrainTrial":
            e.set("text","Delivery_Donkey")
    return root


def semantic(root):
    root = rewrite(root)
    root.find("m_Name").set("text","IDENTITY")
    root.find("m_Description").set("text","")
    return normalize(root)


def stage(out):
    assert not (out/"plan.json").exists(), "Use a fresh output directory"
    out.mkdir(parents=True,exist_ok=True)
    # Protect the human-owned installed build, including loose source content.
    installed = {p.relative_to(WIN_MOD).as_posix():sha(p) for p in WIN_MOD.rglob("*") if p.is_file()}
    (out/"installed-before.json").write_text(json.dumps(installed,indent=2))
    asts = {p.stem:parse(p) for p in (MOD/"Assets").glob("*.ast")}
    for a,b in (("CSC_TRIAL_BAKERS_Delivery_Split","CSC_BAKERS_Storage_Delivery_2_Split"),
                ("CSC_TAILORS_Storage_Delivery_Split","CSC_TAILORS_Storage_Delivery_2_Split")):
        assert semantic(asts[a])==semantic(asts[b]), (a,b,"not duplicates")
    for name in ("CSC_TRIAL_BAKERS_Delivery_Split","CSC_TRIAL_Delivery_Donkey"):
        assert txt(asts[name],"m_BehaviorData/m_dsgName")=="Standard_LandmarkNoRandomOffset"
    retire = {"Assets/"+n+".ast" for n in ALIASES}
    retire.add("Assets/CSC_BAKERS_Storage_Delivery.ast")
    for folder,extensions in (("Geometries",(".geo",".fgx")),("Animations",(".anm",".fgx"))):
        for old in NATIVE:
            retire.update(folder+"/"+old+ext for ext in extensions)
    retire.update(p.relative_to(MOD).as_posix() for p in (MOD/"Geometries").glob("CSC_TEST_TAILORS_Delivery_*"))
    assert len(retire)==18,retire
    sources = {"CSC_BAKERS_Delivery":"CSC_TRIAL_BAKERS_Delivery_Split",
               "CSC_TAILORS_Delivery":"CSC_TAILORS_Storage_Delivery_Split",
               "CSC_ALL_Delivery_Donkey":"CSC_TRIAL_Delivery_Donkey"}
    for new,old in sources.items():
        assert not (MOD/f"Assets/{new}.ast").exists(), "Do not overwrite a new user copy"
        root = rewrite(asts[old])
        assert txt(root,"m_Name")==new
        assert semantic(root)==semantic(asts[old])
        save(root,out/f"staged/Assets/{new}.ast")
    consumers = []
    for name,root in asts.items():
        if f"Assets/{name}.ast" in retire:
            continue
        changed = rewrite(root)
        if normalize(changed)!=normalize(root):
            save(changed,out/f"staged/Assets/{name}.ast")
            consumers.append(name)
    assert len(consumers)==8,consumers
    binary_parity = {}
    for old,new in NATIVE.items():
        for folder,descriptor in (("Geometries",".geo"),("Animations",".anm")):
            dst=out/f"staged/{folder}/{new}.fgx"
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(MOD/f"{folder}/{old}.fgx",dst)
            binary_parity[dst.relative_to(out/"staged").as_posix()] = dict(source=f"{folder}/{old}.fgx",sha256=sha(dst))
            root=parse(MOD/f"{folder}/{old}{descriptor}")
            root.find("m_Name").set("text",new)
            root.find("m_Description").set("text", "Terrain-following delivery donkey" if "Donkey" in new else "Storage crane and delivery route")
            for e in root.findall("m_DataFiles/Element/m_RelativePath"):
                e.set("text",new+".fgx")
            # Native model, mesh, bone and track IDs are deliberately unchanged.
            save(root,out/f"staged/{folder}/{new}{descriptor}")
    xlp=parse(MOD/"XLPs/CSC_Tilebases.xlp")
    entries=xlp.find("m_Entries")
    old_entries=set(ALIASES)|{"CSC_BAKERS_Storage_Delivery"}
    template=copy.deepcopy(entries[0])
    for e in list(entries):
        if txt(e,"m_EntryID") in old_entries:
            entries.remove(e)
    for name in sources:
        assert not any(txt(e,"m_EntryID")==name for e in entries)
        e=copy.deepcopy(template)
        e.find("m_EntryID").set("text",name)
        e.find("m_ObjectName").set("text",name)
        entries.append(e)
    save(xlp,out/"staged/XLPs/CSC_Tilebases.xlp")
    project=(MOD/"Civ Supply Chains.civ6proj").read_bytes()
    # Preserve generated action CDATA and unrelated project formatting exactly.
    def content(m):
        include=re.search(rb'Include="([^"]+)"',m.group(0)).group(1).decode().replace("\\","/")
        return b"" if include in retire else m.group(0)
    project=re.sub(rb'(?m)^[ \t]*<Content Include="[^"]+"[^>]*>.*?</Content>\r?\n',content,project,flags=re.S)
    added=[]
    for p in (out/"staged").rglob("*"):
        if p.suffix in (".ast",".geo",".anm",".fgx"):
            rel=str(p.relative_to(out/"staged")).replace("/","\\")
            if f'Include="{rel}"'.encode() not in project:
                added.append(f'    <Content Include="{rel}">\r\n      <SubType>Content</SubType>\r\n    </Content>\r\n')
    if added:
        project=project.replace(b"  <Import Project=",("  <ItemGroup>\r\n"+"".join(added)+"  </ItemGroup>\r\n").encode()+b"  <Import Project=",1)
    E.fromstring(project)
    (out/"staged/Civ Supply Chains.civ6proj").write_bytes(project)
    # Check the resulting complete runtime graph, excluding historical tools/docs.
    effective={p.relative_to(MOD).as_posix():p for folder in ("Assets","Geometries","Animations","ArtDefs","XLPs")
               for p in (MOD/folder).glob("*") if p.is_file() and p.relative_to(MOD).as_posix() not in retire}
    effective.update({p.relative_to(out/"staged").as_posix():p for p in (out/"staged").rglob("*") if p.is_file()})
    refs=[]
    forbidden=set(ALIASES)|{"CSC_BAKERS_Storage_Delivery","CSC_ALL_Delivery_Pivot"}
    for rel,p in effective.items():
        if p.suffix in (".ast",".xlp",".artdef"):
            r=parse(p)
            for tag in ("m_EntryName","m_GeoName","m_AnimationName","m_EntryID"):
                for e in r.findall(".//"+tag):
                    assert e.get("text") not in forbidden,(rel,tag,e.get("text"))
                    if "Delivery" in (e.get("text") or ""):
                        refs.append((rel,tag,e.get("text")))
    touched=set(retire)|{p.relative_to(out/"staged").as_posix() for p in (out/"staged").rglob("*") if p.is_file()}
    baseline={}
    for rel in touched:
        p=MOD/rel
        baseline[rel]=sha(p) if p.exists() else None
        if p.exists():
            dst=out/"before"/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dst)
    (out/"plan.json").write_text(json.dumps(dict(retire=sorted(retire),baseline=baseline,
        consumers=consumers,sources=sources,binary_parity=binary_parity,references=refs),indent=2))
    print("STAGED: 3 canonical assets; 8 district consumers; 18 obsolete files; four binaries byte-identical",flush=True)


def publish(out):
    plan=json.loads((out/"plan.json").read_text())
    assert (out/"cook-validation.json").exists()
    for rel,h in plan["baseline"].items():
        p=MOD/rel
        assert (sha(p) if p.exists() else None)==h,("changed since snapshot",rel)
    cache_path=Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    raw=cache_path.read_bytes()
    cache=json.loads(raw.decode("utf-8-sig"))
    retired={"Civ Supply Chains/"+r for r in plan["retire"]}
    # Discard metadata for obsolete entries; preserve all unrelated records.
    cache["Files"]=[e for e in cache["Files"] if e["Filename"].replace("\\","/") not in retired]
    cache["Dependencies"]={k:v for k,v in cache["Dependencies"].items() if k.replace("\\","/") not in retired}
    index={(Path(e["Filename"]).suffix.lower(),Path(e["Filename"]).stem.casefold()):e["Filename"].replace("\\","/") for e in cache["Files"]}
    files=[p for p in (out/"staged").rglob("*") if p.is_file()]
    for p in files:
        index[(p.suffix.lower(),p.stem.casefold())]="Civ Supply Chains/"+p.relative_to(out/"staged").as_posix()
    records={e["Filename"].replace("\\","/"):e for e in cache["Files"]}
    now=int(time.time()*10000000)+116444736000000000
    for p in files:
        if p.suffix not in (".ast",".geo",".anm"):
            continue
        r=parse(p); key="Civ Supply Chains/"+p.relative_to(out/"staged").as_posix()
        deps={str(Path(key).parent/e.get("text")).replace("\\","/") for e in r.findall("m_DataFiles/Element/m_RelativePath")}
        for tag,ext in (("m_EntryName",".ast"),("m_GeoName",".geo"),("m_AnimationName",".anm"),("m_dsgName",".dsg")):
            for e in r.findall(".//"+tag):
                if e.get("text"):
                    deps.add(index[(ext,e.get("text").replace("\\","/").split("/")[-1].casefold())])
        for e in r.findall(".//Element"):
            obj,kind=e.find("m_ObjectName"),e.find("m_eObjectType")
            if obj is not None and kind is not None and obj.get("text"):
                ext={"MATERIAL":".mtl","TEXTURE":".tex","GEOMETRY":".geo"}.get(kind.text)
                if ext:
                    deps.add(index[(ext,obj.get("text").replace("\\","/").split("/")[-1].casefold())])
        entry=dict(Filename=key,Timestamp=now,Status=0,Type=2,EntityType={".ast":0,".geo":2,".anm":4}[p.suffix],
                   EntityClass=txt(r,"m_ClassName"),Filesize=p.stat().st_size,Tags=[e.get("text") for e in r.findall("m_Tags/Element")],Stats={})
        if key in records:records[key].update(entry)
        else:cache["Files"].append(entry)
        cache["Dependencies"][key]=sorted(deps)
    # Other dependency lists (including XLP records) may mention retired identities.
    path_alias={"Civ Supply Chains/Assets/"+a+".ast":"Civ Supply Chains/Assets/"+b+".ast" for a,b in ALIASES.items()}
    for old,new in NATIVE.items():
        for folder,exts in (("Geometries",(".fgx",".geo")),("Animations",(".fgx",".anm"))):
            for ext in exts:path_alias[f"Civ Supply Chains/{folder}/{old}{ext}"]=f"Civ Supply Chains/{folder}/{new}{ext}"
    for key,deps in cache["Dependencies"].items():
        cache["Dependencies"][key]=sorted({path_alias.get(d.replace("\\","/"),d) for d in deps
            if d.replace("\\","/") not in retired or d.replace("\\","/") in path_alias})
    cache["Timestamp"]=now
    (out/"AssetCloud-before.json").write_bytes(raw)
    assert cache_path.read_bytes()==raw
    for p in files:
        target=MOD/p.relative_to(out/"staged")
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target)
    for rel in plan["retire"]:
        target=(MOD/rel).resolve()
        assert target.is_relative_to(MOD.resolve()) and target.is_file()
        assert (out/"before"/rel).is_file()
        target.unlink()  # Exact audited files only; no recursive deletion.
    cache_path.write_text(json.dumps(cache,separators=(",",":")),encoding="utf-8")
    for rel,entry in plan["binary_parity"].items():assert sha(MOD/rel)==entry["sha256"]
    original=json.loads((out/"installed-before.json").read_text())
    current={p.relative_to(WIN_MOD).as_posix():sha(p) for p in WIN_MOD.rglob("*") if p.is_file()}
    assert current==original,"Installed game files changed"
    (out/"publish-validation.json").write_text(json.dumps(dict(installed_files_unchanged=len(current),removed=plan["retire"],binary_parity=True),indent=2))
    print("PUBLISHED: canonical source and AssetCloud cleaned; installed game files unchanged")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("stage","publish"));p.add_argument("--output",required=True,type=Path)
    args=p.parse_args();{"stage":stage,"publish":publish}[args.phase](args.output)
