"""Build a review package using Firaxis' manifest task and existing cooked art.

This is a gameplay/UI test package, not a new art cook or Workshop publication.
The installed CSC package is read-only until an explicit --install step.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
NS='http://schemas.microsoft.com/developer/msbuild/2003'
ET.register_namespace('',NS)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--task-assembly',type=Path,required=True)
    parser.add_argument('--msbuild',type=Path,required=True)
    args=parser.parse_args()
    project=ET.parse(ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj').getroot()
    package=args.output.resolve()/'package'/'Civ Supply Chains'
    # Never delete or overwrite an installed tree. Rebuild only this designated
    # output package; all source and installed inputs remain read-only.
    assert package.is_relative_to(args.output.resolve()) and package!=args.installed.resolve()
    if package.exists(): shutil.rmtree(package)
    package.mkdir(parents=True)
    for content in project.findall('.//{'+NS+'}Content'):
        relative=Path(content.attrib['Include'])
        source=ROOT/'Civ Supply Chains'/relative
        target=package/relative
        assert target.resolve().is_relative_to(package)
        if not source.is_file(): raise FileNotFoundError(source)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    for name in ['Platforms','ArtDefs']:
        shutil.copytree(args.installed/name,package/name,dirs_exist_ok=True)
    for file in args.installed.glob('*.dep'): shutil.copy2(file,package/file.name)
    props={child.tag.split('}')[-1]:(child.text or '')
           for group in project.findall('{'+NS+'}PropertyGroup') if 'Condition' not in group.attrib
           for child in group}
    task_project=ET.Element('{'+NS+'}Project',{'ToolsVersion':'4.0','DefaultTargets':'Manifest'})
    ET.SubElement(task_project,'{'+NS+'}UsingTask',{'TaskName':'Firaxis.VisualStudio.Tasks.Civ6.GenerateModInfo','AssemblyFile':str(args.task_assembly)})
    items=ET.SubElement(task_project,'{'+NS+'}ItemGroup')
    ET.SubElement(items,'{'+NS+'}ModFiles',{'Include':str(package/'**'/'*')})
    target=ET.SubElement(task_project,'{'+NS+'}Target',{'Name':'Manifest'})
    fields=['Name','Teaser','Description','Authors','SpecialThanks','Homepage','AffectsSavedGames',
            'SupportsSinglePlayer','SupportsMultiplayer','SupportsHotSeat','CompatibleVersions',
            'ActionCriteriaData','LocalizedTextData','FrontEndActionData','InGameActionData','AssociationData']
    attributes={field:props.get(field,'') for field in fields}
    attributes.update(ID=props['Guid'],Version=props['ModVersion'],CustomProperties=props.get('ModProperties',''),
                      Files='@(ModFiles)',TargetPath=str(package/'Civ Supply Chains.modinfo'))
    ET.SubElement(target,'{'+NS+'}GenerateModInfo',attributes)
    generated=args.output/'manifest.proj'
    ET.ElementTree(task_project).write(generated,encoding='utf-8',xml_declaration=True)
    command=[str(args.msbuild),str(generated),'/nologo','/verbosity:minimal']
    result=subprocess.run(command,capture_output=True,text=True)
    (args.output/'package-build.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode: print(result.stdout,result.stderr); raise SystemExit(result.returncode)
    manifest=ET.parse(package/'Civ Supply Chains.modinfo').getroot()
    text=(package/'Civ Supply Chains.modinfo').read_text(encoding='utf-8-sig')
    assert 'eaffc7c2-21d2-47e5-a060-ae55780d1337' not in text
    assert 'Ruivo_Adjacencies/' not in text
    declared=[f.text for f in manifest.findall('.//Files/File')]
    for file in declared: assert (package/file).is_file(),file
    hashes={str(f.relative_to(package)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest()
            for f in package.rglob('*') if f.is_file()}
    (args.output/'package-files.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(hashes)} files with native Firaxis manifest task: {package}')
    print('No MAB dependency or legacy patch helper in package.')


if __name__=='__main__': main()
