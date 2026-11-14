"""Read-only qualification of the loaded material/provider stack and map census.

This inspects Firaxis's actual SQLite export and live map facts; it changes no
bids, ownership, visibility or game properties. Definitions loading is distinct
from native AI consumption. Resource provenance uses producer declarations,
never an identifier prefix. Literal SQL/XML declarations are recognised; dynamic
SELECT generation is reported as unresolved rather than guessed.
"""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

GAME_ROOT = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI")
SR_ID = '37fdca0b-9275-4235-9c18-c7ec348f930e'
CL_ID = '95b955fc-2dd1-41c5-989e-0265d98a28bd'
CSC_IDS = {'c5e66bd1-d804-443b-ac3d-1917a20dba3c', 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a17'}
# Current CL rural roots and named replacement aliases. The loaded replacement
# graph below also covers future aliases; absent definitions are not demanded.
PROVIDER_ALIASES = {
    'DISTRICT_RURALCOMMUNITYA', 'DISTRICT_RURALCOMMUNITYB', 'DISTRICT_RURALCOMMUNITYC',
    'DISTRICT_COREX_FRONTIER_TOWN', 'DISTRICT_COREX_TROYU',
    'DISTRICT_COREX_TSIKHE', 'DISTRICT_COREX_GYOSON',
}
TOKEN = re.compile(r"--[^\r\n]*|/\*[\s\S]*?\*/|'(?:''|[^'])*'|\"[^\"]*\"|\[[^\]]*\]|`[^`]*`|[A-Za-z_][A-Za-z_0-9]*|[^\s]", re.M)


def _identifier(token):
    return token.strip('"`[]').upper()


def _literal(token):
    return token[1:-1].replace("''", "'") if token.startswith("'") else None


def declared_resources(path):
    """Return literal Resources producers and unresolved-statement evidence.

    Type registrations, modifier references and UPDATE/DELETE mentions are not
    resource producers. INSERT SELECT literals (including Suk's Gold replacement)
    count; nonliteral source-table copies remain explicitly unresolved.
    """
    path = Path(path)
    text = path.read_text(encoding='utf-8-sig', errors='replace')
    names, unresolved = set(), []
    if path.suffix.lower() == '.xml':
        if not re.search(r'<Resources(?:\s|>)', text):
            return names, unresolved
        try:
            root = ET.fromstring(text)
        except ET.ParseError as error:
            return names, [str(error)]
        for table in root.iter('Resources'):
            for row in table.findall('Row'):
                name = row.get('ResourceType') or row.findtext('ResourceType')
                if name:
                    names.add(name)
        return names, unresolved
    tokens = [m.group() for m in TOKEN.finditer(text) if not m.group().startswith(('--', '/*'))]
    statements, current = [], []
    for token in tokens:
        if token == ';':
            statements.append(current); current = []
        else:
            current.append(token)
    statements.append(current)
    for tokens in statements:
        upper = [_identifier(t) for t in tokens]
        if not upper or upper[0] != 'INSERT' or 'INTO' not in upper:
            continue
        into = upper.index('INTO')
        if into + 2 >= len(tokens) or upper[into + 1] != 'RESOURCES':
            continue
        pos = into + 2
        if tokens[pos] != '(':
            unresolved.append('Resources INSERT without explicit columns'); continue
        close = tokens.index(')', pos)
        columns = [t for t in upper[pos + 1:close] if t != ',']
        if 'RESOURCETYPE' not in columns:
            continue
        resource_column = columns.index('RESOURCETYPE')
        payload = tokens[close + 1:]
        rows = []
        if payload and _identifier(payload[0]) == 'VALUES':
            depth, row, cell = 0, [], []
            for token in payload[1:]:
                if token == '(':
                    depth += 1
                    if depth == 1:
                        row, cell = [], []; continue
                if token == ')':
                    depth -= 1
                    if depth == 0:
                        row.append(cell); rows.append(row); continue
                if token == ',' and depth == 1:
                    row.append(cell); cell = []
                elif depth:
                    cell.append(token)
        elif payload and _identifier(payload[0]) == 'SELECT':
            row, cell, depth = [], [], 0
            for token in payload[1:]:
                if depth == 0 and _identifier(token) == 'FROM':
                    break
                if token == ',' and depth == 0:
                    row.append(cell); cell = []
                else:
                    cell.append(token)
                    if token == '(' : depth += 1
                    if token == ')' : depth -= 1
            row.append(cell); rows.append(row)
        for row in rows:
            value = row[resource_column] if resource_column < len(row) else []
            name = _literal(value[0]) if len(value) == 1 else None
            if name:
                names.add(name)
            else:
                unresolved.append('Nonliteral Resources.ResourceType expression')
        if not rows:
            unresolved.append('Unrecognised Resources producer')
    return names, unresolved


def _source_files(path, files=None):
    path = Path(path)
    paths = (path / name for name in files) if files is not None else path.rglob('*')
    return sorted(p for p in paths if p.is_file() and p.suffix.lower() in ('.sql', '.xml'))


def _vanilla_sources():
    roots = (GAME_ROOT / 'Base/Assets/Gameplay/Data', GAME_ROOT / 'DLC')
    # Australia Scenario declares Gold, but that is not a producer in ordinary
    # XP2 games. Including it would mislabel Suk's normal-game Gold as vanilla.
    return sorted({p for root in roots for p in root.rglob('*Resources*')
                   if p.is_file() and p.suffix.lower() in ('.sql', '.xml')
                   and not any('scenario' in part.lower() for part in p.relative_to(GAME_ROOT).parts)})


def _lua_table(values):
    # JSON string escapes used here are valid Lua for actual resource identifiers
    # and the fixed ASCII classifications. No arbitrary source text is executed.
    return '{' + ','.join('[' + json.dumps(k) + ']=' + json.dumps(v)
                          for k, v in sorted(values.items())) + '}'


def _read_database(path):
    path = Path(path).resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        resources = {r[0] for r in db.execute('SELECT ResourceType FROM Resources')}
        tags = {}
        for name, tag in db.execute('SELECT Type,Tag FROM TypeTags'):
            tags.setdefault(tag, set()).add(name)
        improvements = {r[0] for r in db.execute('SELECT ImprovementType FROM Improvements')}
        mappings = {}
        for name, improvement in db.execute('SELECT ResourceType,ImprovementType FROM Improvement_ValidResources'):
            if improvement in improvements:
                mappings.setdefault(name, set()).add(improvement)
        districts = {r[0] for r in db.execute('SELECT DistrictType FROM Districts')}
        replacements = list(db.execute('SELECT CivUniqueDistrictType,ReplacesDistrictType FROM DistrictReplaces'))
    return resources, tags, mappings, districts, replacements


def _census_code():
    return r'''-- Passive preflight census: no policy state, events or game orders.
local counts={}
for i=0,Map.GetPlotCount()-1 do
 local plot=Map.GetPlotByIndex(i)
 local resource=GameInfo.Resources[plot:GetResourceType()]
 if resource then
  local row=counts[resource.ResourceType]or{0,0};counts[resource.ResourceType]=row
  row[1]=row[1]+1
  local player=Players[plot:GetOwner()]
  if player and player:IsMajor() and not player:IsHuman()then row[2]=row[2]+1 end
 end
end
print('CSC_RESOURCE_STACK_BEGIN\t'..Game.GetCurrentGameTurn())
local names={};for name in pairs(counts)do names[#names+1]=name end;table.sort(names)
for _,name in ipairs(names)do
 print('CSC_RESOURCE_STACK_ROW\t'..name..'\t'..counts[name][1]..'\t'..counts[name][2])
end
print('CSC_RESOURCE_STACK_END\t'..#names)
'''


def _parse_census(raw):
    begin = re.findall(r'CSC_RESOURCE_STACK_BEGIN\t(\d+)', raw)
    end = re.findall(r'CSC_RESOURCE_STACK_END\t(\d+)', raw)
    rows = re.findall(r'CSC_RESOURCE_STACK_ROW\t([^\t\r\n]+)\t(\d+)\t(\d+)', raw)
    if len(begin) != 1 or len(end) != 1 or len(rows) != int(end[0]) or len({r[0] for r in rows}) != len(rows):
        raise AssertionError('Missing, duplicate or incomplete read-only resource census')
    return int(begin[0]), {name: dict(map=int(total), ai_owned=int(owned)) for name, total, owned in rows}


def inspect_resource_stack(controller, out, user_root, extra_mods, *, csc_path=None):
    """Write evidence and return origins/counts; reject missing loaded mappings.

    Pass the staged main CSC path explicitly. Fallback discovery accepts only
    the canonical or documented local development mod id. Selected extra_mods
    are id -> {path, files}; files may be a filename list or hash manifest dict.
    Absent material instances limit a seed's coverage but never reject the seed.
    """
    out, user_root = Path(out), Path(user_root)
    out.mkdir(parents=True, exist_ok=True)
    database = user_root / 'Cache/DebugGameplay.sqlite'
    resources, tags, mappings, districts, replacements = _read_database(database)
    errors, warnings, unused_tags, groups = [], [], {}, {}
    for family in ('BAKERS', 'TAILORS'):
        for kind in ('BASE', 'SPEC'):
            tag = 'CLASS_CSC_' + family + '_' + kind
            names = tags.get(tag, set()) & resources
            groups[tag] = sorted(names)
            if not names:
                errors.append('No loaded resources for ' + tag)
            for name in sorted(names):
                if not mappings.get(name):
                    errors.append('No valid loaded improvement for ' + tag + ':' + name)
            dangling = tags.get(tag, set()) - resources
            if dangling:
                # Compatibility files can retain a tag for an alias removed by
                # another selected mod (R2 GOLD2 after Suk replaces it with GOLD).
                # These declarations cannot identify map resources or suppliers.
                # Keep them as evidence; validate only the actual loaded class
                # resources and their improvement mappings above.
                unused_tags[tag] = sorted(dangling)
                warnings.append('Unused TypeTags without Resources definitions for '
                                + tag + ':' + ','.join(sorted(dangling)))
    sr_selected = SR_ID in {str(mid).lower() for mid in extra_mods}
    if sr_selected and ('RESOURCE_GOLD' not in tags.get('CLASS_CSC_TAILORS_SPEC', set())
                        or 'IMPROVEMENT_MINE' not in mappings.get('RESOURCE_GOLD', set())):
        errors.append('Suk Gold replacement lacks final Tailors SPEC tag or Mine mapping')
    aliases = (PROVIDER_ALIASES | {d for d in districts if d.startswith('DISTRICT_RURALCOMMUNITY')}) & districts
    while True:
        expanded = aliases | {unique for unique, base in replacements if base in aliases and unique in districts}
        if expanded == aliases:
            break
        aliases = expanded
    cl_selected = CL_ID in {str(mid).lower() for mid in extra_mods}
    if cl_selected and not aliases:
        errors.append('City Lights selected but no rural/provider district definitions loaded')
    for district in sorted(aliases):
        for family in ('BAKERS', 'TAILORS'):
            if district not in tags.get('CLASS_CSC_' + family + '_GOODS_PROVIDER', set()):
                errors.append('Missing ' + family + ' goods-provider mapping for ' + district)
    producers, unresolved = {}, []
    def collect(paths, producer):
        for path in paths:
            names, issues = declared_resources(path)
            for name in names:
                producers.setdefault(name, set()).add(producer)
            unresolved.extend(dict(path=str(path), issue=issue) for issue in issues)
    collect(_vanilla_sources(), 'vanilla')
    for mid, mod in extra_mods.items():
        collect(_source_files(mod['path'], mod.get('files')), str(mid))
    if csc_path is None:
        for metadata in (user_root / 'Mods').glob('*/*.modinfo'):
            try:
                if ET.parse(metadata).getroot().get('id', '').lower() in CSC_IDS:
                    if csc_path is not None:
                        raise AssertionError('Multiple installed CSC packages; pass csc_path explicitly')
                    csc_path = metadata.parent
            except ET.ParseError:
                continue
    if csc_path is not None:
        collect(_source_files(csc_path), 'CSC')
    origins = {name: 'vanilla' if 'vanilla' in producers.get(name, set()) else
               'modded' if producers.get(name) else 'unknown' for name in sorted(resources)}
    (out / 'resource-origins.lua').write_text(_lua_table(origins) + '\n', encoding='utf-8')
    census_code = _census_code()
    (out / 'resource-stack-census.lua').write_text(census_code, encoding='utf-8')
    # Persist database/declaration errors before rejection; do not run a live
    # census for a broken loaded stack or accidentally qualify a stale export.
    result = dict(database=str(database), database_sha256=hashlib.sha256(database.read_bytes()).hexdigest(),
                  groups=groups, improvements={n: sorted(mappings.get(n, set())) for n in resources},
                  city_lights_providers=sorted(aliases), origins=origins,
                  origin_sources={n: sorted(producers.get(n, set())) for n in resources},
                  unresolved_declarations=unresolved, unused_material_tags=unused_tags,
                  warnings=warnings, errors=errors)
    evidence = out / 'resource-stack-preflight.json'
    evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if errors:
        raise AssertionError('Resource stack preflight failed: ' + '; '.join(errors))
    raw = controller.cmd(census_code, 'CSC_AI_BakersGameplay', 'read-only-resource-stack-census')
    (out / 'resource-stack-census.txt').write_text(raw, encoding='utf-8')
    turn, counts = _parse_census(raw)
    for name in resources:
        counts.setdefault(name, dict(map=0, ai_owned=0))
    result.update(turn=turn, counts=counts, verified=True,
                  groups_census={tag: dict(map=sum(counts[n]['map'] for n in names),
                                          ai_owned=sum(counts[n]['ai_owned'] for n in names))
                                 for tag, names in groups.items()},
                  limits=['No map instances for ' + tag for tag, names in groups.items()
                          if not any(counts[n]['map'] for n in names)])
    evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return result
