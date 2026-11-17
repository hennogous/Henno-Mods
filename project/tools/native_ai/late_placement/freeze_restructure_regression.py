"""Build committed CSC through SDK packaging, reusing qualified cooked art.

This is a source/action regression package, not an art-cooker qualification.
Every declared Content input comes from the requested commit; existing cooked
art and the exact CE binary come from the accepted comparison package. No live
Mods directory is touched. The shared controller alone installs/restores it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def freeze(repo, base, output, revision='HEAD'):
    repo,base,output=(Path(p).resolve() for p in (repo,base,output))
    if output.exists():
        raise ValueError('Require a new output directory')
    commit=subprocess.check_output(['git','-C',str(repo),'rev-parse',revision]).decode().strip()
    def content(path):
        return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])
    source=content('Civ Supply Chains/Civ Supply Chains.civ6proj').decode('utf-8-sig')
    document=ET.fromstring(source)
    paths=[row.attrib['Include'] for row in document.findall('.//{*}Content')]
    if len(paths)!=len({p.replace('\\','/').casefold() for p in paths}):
        raise ValueError('Duplicate native Content destination')
    output.mkdir(parents=True)
    inputs=output/'sdk-inputs';inputs.mkdir()
    hashes={}
    for relative in paths:
        target=(inputs/relative).resolve()
        if not target.is_relative_to(inputs):raise ValueError('Content outside isolated inputs')
        data=content('Civ Supply Chains/'+relative.replace('\\','/'))
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        hashes[relative.replace('\\','/')]=hashlib.sha256(data).hexdigest()
    frozen=output/'frozen';frozen.mkdir()
    shutil.copytree(base/'CE',frozen/'CE')
    # The SDK Build target performs Clean, Content copy and GenerateModInfo.
    # Override only its art-cooking callback, preserving the reviewed cooked
    # assets. Both Clean destinations are explicit children of this new output.
    package=frozen/'CSC';native_output=output/'sdk-output'/'Civ Supply Chains'
    assert native_output.is_relative_to(output) and not native_output.exists()
    ns='http://schemas.microsoft.com/developer/msbuild/2003'
    target=ET.SubElement(document,'{'+ns+'}Target',Name='CheckCookAssets')
    ET.SubElement(target,'{'+ns+'}Message',Text='Reusing accepted cooked art; no art recook in this regression.')
    items=ET.SubElement(target,'{'+ns+'}ItemGroup')
    ET.SubElement(items,'{'+ns+'}_AcceptedArt',Include=str(base/'CSC/Platforms'/'**/*'))
    ET.SubElement(target,'{'+ns+'}Copy',SourceFiles='@(_AcceptedArt)',
        DestinationFiles='$(BuildDir)\\Platforms\\%(_AcceptedArt.RecursiveDir)%(_AcceptedArt.Filename)%(_AcceptedArt.Extension)')
    ET.SubElement(target,'{'+ns+'}Copy',SourceFiles=str(base/'CSC/Civ_Supply_Chains.dep'),
        DestinationFolder='$(BuildDir)')
    project=inputs/'Civ Supply Chains.civ6proj'
    ET.register_namespace('',ns)
    ET.ElementTree(document).write(project,encoding='utf-8',xml_declaration=True)
    sdk=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK/ModBuddy/Extensions/Application")
    command=[r'C:/Program Files (x86)/MSBuild/12.0/Bin/MSBuild.exe',str(project),
        '/nologo','/verbosity:minimal','/t:Build',
        '/p:MSBuildLocalExtensionPath='+str(sdk)+'\\',
        '/p:Civ6_UserPath='+str(output/'isolated-user'),
        '/p:BuildDir='+str(native_output),'/p:OutputDir='+str(native_output),
        '/p:ModInfoPath='+str(native_output/'Civ Supply Chains.modinfo')]
    result=subprocess.run(command,capture_output=True,text=True,errors='replace')
    (output/'sdk-build.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('SDK build failed; see '+str(output/'sdk-build.log'))
    shutil.move(str(native_output),package)
    manifest,=package.glob('*.modinfo');mod=ET.parse(manifest).getroot()
    for action in mod.find('InGameActions'):
        for file in action.findall('File'):
            if not (package/file.text).is_file():raise ValueError('Unpackaged action input '+str(file.text))
    proxy,=(frozen/'CE/Binaries/Win64').glob('GameCore_XP2_CE*.dll')
    record=dict(commit=commit,base=str(base),content_sha256=hashes,
        ce_sha256=hashlib.sha256(proxy.read_bytes()).hexdigest(),
        manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        sdk_exit_code=result.returncode,art_reused=True,unrelated_workspace_content_included=False)
    (output/'freeze.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(frozen=str(frozen),commit=commit,content_files=len(hashes),ce_sha256=record['ce_sha256'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('repo','base','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--revision',default='HEAD')
    freeze(**vars(parser.parse_args()))
