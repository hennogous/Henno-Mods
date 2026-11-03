"""Pure CSC native-probe artifact and narrow package-staging helpers.

No process, game, network or filesystem action on import. Callers supply exact
baseline manifests, owner inventory and metadata writer. Heavy immutable inputs
stay hash/path references; explicit two/three/four-file staging preserves unknown concurrent edits.
"""
import hashlib
import os
import shutil
import traceback
from pathlib import Path

RELATIVES = ('Lua_UI/AI/CSC_AI_Assistance.lua', 'Lua_UI/AI/CSC_AI_OpportunityPolicy.lua')
THREE_AI_RELATIVES = RELATIVES + ('ModSupport/ModSupport_RH_AI.sql',)
FOUR_AI_RELATIVES = RELATIVES + ('ModSupport/ModSupport_RH_AI.sql', 'ModSupport/ModSupport_RH_AI_Roles.lua')
V2_FIVE_AI_RELATIVES = RELATIVES + ('Lua_UI/AI/CSC_AI_AssistanceUI.lua', 'Data/CSC_AI.sql', 'ModSupport/ModSupport_RH_AI.sql')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def archive_sources(pins, directory):
    """Archive code and small metadata; immutable heavy inputs stay hash/path."""
    allowed = {'.py', '.lua', '.sql', '.xml', '.json', '.md'}
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


def _stage_files(sources, installed, deployment, baseline, manifest, inventory, write):
    """Back up and prepare ALL declared files before atomic file replacements.

    A failure restores only the declared known old/new byte identities, with native
    absence and an unchanged remainder of the original package independently
    checked. Unknown edits are preserved and reported for reconciliation.
    """
    relatives = tuple(sources)
    expected = dict(baseline)
    write(deployment / 'original-installed-manifest.json', baseline)
    for relative in relatives:
        source = sources[relative]
        expected[str(Path(relative))] = dict(sha256=sha(source), size=source.stat().st_size)
    write(deployment / 'expected-installed-manifest.json', expected)
    try:
        for relative in relatives:
            destination = installed / relative; destination.resolve().relative_to(installed)
            backup = deployment / 'backup' / relative; backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
            if dict(sha256=sha(backup), size=backup.stat().st_size) != baseline[str(Path(relative))]:
                raise RuntimeError('Original approved-file backup mismatch')
        for relative in relatives:
            temporary = deployment / 'prepared' / relative; temporary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sources[relative], temporary)
            if dict(sha256=sha(temporary), size=temporary.stat().st_size) != expected[str(Path(relative))]:
                raise RuntimeError('Prepared candidate hash mismatch')
        if inventory() or manifest(installed) != baseline:
            raise RuntimeError('Owner/package changed before atomic narrow stage')
        for relative in relatives:
            os.replace(deployment / 'prepared' / relative, installed / relative)
        if manifest(installed) != expected:
            raise RuntimeError('Unexpected installed delta after narrow stage')
        write(deployment / 'deployment.json', dict(changed=list(relatives), narrow_file_stage=True, file_count=len(relatives), all_backed_up_before_writes=True))
        return expected
    except BaseException as failure:
        write(deployment / 'stage-failure.json', dict(error=str(failure), traceback=traceback.format_exc()))
        current = manifest(installed)
        changed_names = {str(Path(r)) for r in relatives}
        known = set(current) == set(baseline) and all(
            current[k] in (baseline[k], expected[k]) if k in changed_names else current[k] == baseline[k]
            for k in baseline)
        if inventory() or not known:
            raise RuntimeError('Partial staging cannot restore: unknown owner/bytes preserved') from failure
        for relative in relatives:
            key = str(Path(relative))
            if current[key] != baseline[key]:
                backup = deployment / 'backup' / relative
                if not backup.exists() or dict(sha256=sha(backup), size=backup.stat().st_size) != baseline[key]:
                    raise RuntimeError('Partial staging backup unavailable; preserve known stage') from failure
                shutil.copy2(backup, installed / relative)
        if manifest(installed) != baseline:
            raise RuntimeError('Partial-stage exact original restoration failed') from failure
        write(deployment / 'partial-stage-restored.json', dict(verified=True, files=len(baseline), known_approved_file_bytes_only=True))
        raise


def stage_two_files(repo, installed, deployment, baseline, manifest, inventory, write):
    sources={relative:Path(repo)/'Civ Supply Chains'/relative for relative in RELATIVES}
    return _stage_files(sources,installed,deployment,baseline,manifest,inventory,write)


def stage_three_ai_files(sources, installed, deployment, baseline, manifest, inventory, write):
    normalized={Path(k).as_posix():Path(v) for k,v in sources.items()}
    if set(normalized)!=set(THREE_AI_RELATIVES):
        raise ValueError('Only the three declared existing AI files may be staged')
    return _stage_files({key:normalized[key] for key in THREE_AI_RELATIVES},installed,deployment,baseline,manifest,inventory,write)


def stage_four_ai_files(sources, installed, deployment, baseline, manifest, inventory, write):
    normalized={Path(k).as_posix():Path(v) for k,v in sources.items()}
    if set(normalized)!=set(FOUR_AI_RELATIVES):
        raise ValueError('Only the four declared existing AI files may be staged')
    return _stage_files({key:normalized[key] for key in FOUR_AI_RELATIVES},installed,deployment,baseline,manifest,inventory,write)


def stage_v2_ai_files(sources, installed, deployment, baseline, manifest, inventory, write):
    """Exactly four v2 replacements plus the unchanged direct-Granary SQL append."""
    normalized={Path(k).as_posix():Path(v) for k,v in sources.items()}
    if set(normalized)!=set(V2_FIVE_AI_RELATIVES):
        raise ValueError('Only the five declared v2 existing AI files may be staged')
    return _stage_files({key:normalized[key] for key in V2_FIVE_AI_RELATIVES},installed,deployment,baseline,manifest,inventory,write)


def _compose_ai_overlay(relatives, payloads, installed, output, baseline, review_sources, write):
    """Prepare declared text inputs; append trial payloads to exact installed bases."""
    installed=Path(installed);output=Path(output)
    if set(review_sources)!=set(relatives)-set(payloads):
        raise ValueError('Require exactly the declared replacement source inputs')
    result={};provenance=[]
    for relative in relatives:
        base=installed/relative
        if dict(sha256=sha(base),size=base.stat().st_size)!=baseline[str(Path(relative))]:
            raise RuntimeError('Installed baseline changed before overlay composition')
        if relative in payloads:
            payload=Path(payloads[relative]);data=base.read_bytes()+b'\n'+payload.read_bytes()
            evidence=dict(relative=relative,base_sha256=sha(base),append_sha256=sha(payload),mode='append_only')
        else:
            source=Path(review_sources[relative]);data=source.read_bytes()
            evidence=dict(relative=relative,source_sha256=sha(source),mode='review_host_replacement')
        destination=output/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists()and destination.read_bytes()!=data:
            raise RuntimeError('Existing prepared overlay differs; use a new output directory')
        if not destination.exists():destination.write_bytes(data)
        result[relative]=str(destination.resolve());provenance.append(dict(evidence,prepared_sha256=sha(destination),bytes=len(data)))
    write(output/'overlay-provenance.json',dict(files=provenance,installed_written=False,modinfo_changed=False,new_mod_ids=False))
    return result



def compose_three_ai_overlay(installed, output, baseline, review_sources, sql_append, write):
    """Review two hosts and append SQL; the Roles Lua remains untouched."""
    return _compose_ai_overlay(THREE_AI_RELATIVES,{'ModSupport/ModSupport_RH_AI.sql':sql_append},installed,output,baseline,review_sources,write)


def compose_four_ai_overlay(installed, output, baseline, review_sources, sql_append, lua_append, write):
    return _compose_ai_overlay(FOUR_AI_RELATIVES,{'ModSupport/ModSupport_RH_AI.sql':sql_append,'ModSupport/ModSupport_RH_AI_Roles.lua':lua_append},installed,output,baseline,review_sources,write)


def compose_v2_ai_overlay(installed, output, baseline, replacement_sources, granary_sql_append, write):
    """Four exact replacements and the previous direct-Granary append, no Roles edit."""
    return _compose_ai_overlay(V2_FIVE_AI_RELATIVES,{'ModSupport/ModSupport_RH_AI.sql':granary_sql_append},installed,output,baseline,replacement_sources,write)


def restore_known_files(installed, deployment, baseline, expected, relatives, manifest, inventory, write):
    """Restore only the approved exact old/new bytes after native absence."""
    relatives=tuple(Path(r).as_posix() for r in relatives)
    if set(relatives) not in (set(RELATIVES),set(THREE_AI_RELATIVES),set(FOUR_AI_RELATIVES),set(V2_FIVE_AI_RELATIVES)):
        raise ValueError('Unknown restoration scope')
    if inventory()or manifest(installed)!=expected:
        raise RuntimeError('Owner or unknown installed change; preserve files')
    for relative in relatives:
        backup=Path(deployment)/'backup'/relative
        if dict(sha256=sha(backup),size=backup.stat().st_size)!=baseline[str(Path(relative))]:
            raise RuntimeError('Original backup changed; preserve files')
    for relative in relatives:shutil.copy2(Path(deployment)/'backup'/relative,Path(installed)/relative)
    if manifest(installed)!=baseline:raise RuntimeError('Exact original installed baseline not restored')
    write(Path(deployment).parent/'package-restored.json',dict(verified=True,files=len(baseline),only_restored=list(relatives)))



