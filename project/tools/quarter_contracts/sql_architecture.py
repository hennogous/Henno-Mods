"""Offline authoring checks: Quarter terms -> shared compiler -> native consumers.

The shared contract owns file phases and table placement; the manifest supplies
activation conditions. Check grouped actions per file, preserving their criteria.
"""
from pathlib import Path
import re
import yaml
from format_sql_layout import LEXER

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT = 'project/specs/reference/csc-shared-sql.yaml'


def load_contract(root=ROOT, relative=DEFAULT_CONTRACT):
    return yaml.safe_load((root / relative).read_text(encoding='utf-8'))


def statements(text):
    """Yield code tokens/positions without interpreting comments or literal contents."""
    tokens = [token for token in LEXER.finditer(text) if token.lastgroup not in ('space', 'comment')]
    start = 0
    for index, token in enumerate(tokens):
        if token.group() == ';':
            yield tokens[start:index + 1]
            start = index + 1


def write_table(tokens):
    words = [token.group().upper() for token in tokens]
    if not words:
        return None
    if words[0] in ('INSERT', 'REPLACE'):
        at = words.index('INTO') if 'INTO' in words else 0
    elif words[0] == 'UPDATE':
        at = 0
    elif words[:2] == ['DELETE', 'FROM']:
        at = 1
    else:
        return None
    return tokens[at + 1].group().strip(chr(96) + '"[]').casefold()


def persistent_table(tokens):
    words = [token.group().upper() for token in tokens]
    if not words or words[0] != 'CREATE' or 'TABLE' not in words[:5]:
        return None
    if 'TEMP' in words[:3] or 'TEMPORARY' in words[:3]:
        return None
    at = words.index('TABLE') + 1
    if words[at:at + 3] == ['IF', 'NOT', 'EXISTS']:
        at += 3
    return tokens[at].group().strip(chr(96) + '"[]').casefold()


def definition_label_errors(text, tokens):
    """Check every literal Districts/Buildings field, including subsequent rows."""
    words = [token.group().upper() for token in tokens]
    at = words.index('INTO')
    opened = words.index('(', at + 2)
    closed = words.index(')', opened + 1)
    if words[closed + 1] != 'VALUES':
        return []
    columns = [token.group() for token in tokens[opened + 1:closed] if token.group() != ',']
    errors = []
    depth = 0
    field = 0
    start = 0
    for token in tokens[closed + 2:]:
        value = token.group()
        if value == '(':
            if depth == 0:
                start, field = token.end(), 0
            depth += 1
        elif value == ')' or (value == ',' and depth == 1):
            if value == ')':
                depth -= 1
            if depth == 0 or (value == ',' and depth == 1):
                fragment = text[start:token.start()]
                if field < len(columns) and not re.search(
                        r'/\*\s*' + re.escape(columns[field]) + r',?\s*\*/', fragment):
                    line = text.count('\n', 0, start) + 1
                    errors.append(f'line {line}: definition value needs its /* {columns[field]}, */ label')
                start = token.end()
                field += 1
    return errors


def validate_core(path, contract=None):
    contract = contract or load_contract()
    text = path.read_text(encoding='utf-8-sig')
    sections = [(match.start(), int(match[1])) for match in re.finditer(
        r'^/\*\t([1-7])\. .+? \*/$', text, re.M)]
    ownership = {name.casefold(): values for name, values in contract['core_sections'].items()}
    generated = {name.casefold() for name in contract['generated_registries']}
    declarations = {name.casefold() for name in contract['declaration_tables']}
    counts = {}
    errors = []
    for tokens in statements(text):
        position = tokens[0].start()
        section = next((value for start, value in reversed(sections) if start <= position), None)
        table = write_table(tokens)
        line = text.count('\n', 0, position) + 1
        words = [token.group().upper() for token in tokens]
        if words[0] == 'INSERT' and table in ('districts', 'buildings'):
            errors.extend(definition_label_errors(text, tokens))
        if persistent_table(tokens):
            errors.append(f'line {line}: persistent tables belong in shared Schema, not Quarter SQL')
        if table in generated:
            errors.append(f'line {line}: {table} is generated; author transaction declarations instead')
        if table in ownership and section not in ownership[table]:
            errors.append(f'line {line}: {table} belongs in section(s) {ownership[table]}, found {section}')
        if table in ('buildings', 'civics') and section == 7:
            if words[0] != 'UPDATE' or 'SET' not in words or words[words.index('SET') + 1] != 'DESCRIPTION':
                errors.append(f'line {line}: section 7 permits only description updates for {table}')
        if table in ('modifiers', 'modifierarguments', 'buildingmodifiers'):
            allowed = (5, 7) if table == 'buildingmodifiers' else (6, 7)
            if section not in allowed:
                errors.append(f'line {line}: {table} belongs in section(s) {allowed}')
            if section == 7 and not re.search(r'STAGE_[234]_(?:ART_PROPERTY|PROP)',
                                             text[tokens[0].start():tokens[-1].end()]):
                errors.append(f'line {line}: section 7 native effects must be Service-gated art properties')
        if table == 'districtmodifiers' and section not in (4, 6):
            errors.append(f'line {line}: district attachments belong in section 4 or 6')
        if table in declarations or (table and table.startswith('csc_') and table.endswith('bindings')):
            counts[table] = counts.get(table, 0) + 1
    for table, count in counts.items():
        if count > 1:
            errors.append(f'{table}: combine {count} declaration batches into one INSERT in this core file')
    return errors


def validate_pipeline(root, contract, actions_document):
    """Check dependencies, including file sequence inside a consolidated action."""
    actions = actions_document.get('blocks', {}).get('inGameActions', [])
    registrations = {}
    for index, action in enumerate(actions):
        for offset, filename in enumerate(action.get('files', [])):
            registrations.setdefault(filename, []).append((action, index, offset))
    positions = {}
    errors = []
    for role, expected in contract['files'].items():
        filename = expected['file']
        if not (root / 'Civ Supply Chains' / filename).is_file():
            errors.append(f'{role}: missing shared input {filename}')
        owners = registrations.get(filename, [])
        if len(owners) != 1:
            errors.append(f'{role}: expected one file registration, found {len(owners)}')
            continue
        action, index, offset = owners[0]
        if action['type'] != 'UpdateDatabase':
            errors.append(f'{role}: shared SQL needs UpdateDatabase')
        if action.get('criteria', []) != expected['criteria']:
            errors.append(f'{role}: incorrect shared SQL criteria')
        actual = action.get('properties', {}).get('LoadOrder')
        if str(actual) != str(expected['load_order']):
            errors.append(f'{role}: expected LoadOrder {expected["load_order"]}, found {actual}')
        try:
            positions[role] = (int(actual), index, offset)
        except (TypeError, ValueError):
            errors.append(f'{role}: shared SQL needs an explicit numeric LoadOrder')
    for earlier, later in zip(contract['dependency_order'], contract['dependency_order'][1:]):
        if earlier in positions and later in positions and positions[earlier] >= positions[later]:
            errors.append(f'{earlier} must load before {later}')
    retired = set(contract['retired_files'])
    for filename in registrations:
        if filename in retired or re.fullmatch(r'Data/CSC_Q_[A-Z]+_TRANSACTIONS(?:_GOLD)?\.sql', filename):
            errors.append(f'retired SQL input still registered: {filename}')
    schema_path = root / 'Civ Supply Chains' / contract['files']['schema']['file']
    common_path = root / 'Civ Supply Chains' / contract['files']['common']['file']
    if schema_path.is_file():
        defined = {persistent_table(tokens) for tokens in statements(schema_path.read_text(encoding='utf-8-sig'))}
        required = set(contract['declaration_tables']) | set(contract['generated_registries'])
        required.update(name for name in contract['core_sections'] if name.endswith('Bindings'))
        for table in sorted(required):
            if table.casefold() not in defined:
                errors.append(f'schema: missing shared table definition {table}')
    if common_path.is_file() and any(persistent_table(tokens) for tokens in statements(
            common_path.read_text(encoding='utf-8-sig'))):
        errors.append('common: persistent table definitions belong in shared Schema')
    # Inspect actual writers, including optional compatibility inputs. Names of
    # actions and files do not establish when their declarations become visible.
    declarations = {table.casefold() for table in contract['declaration_tables']}
    schema, compiler = positions.get('schema'), positions.get('transactions')
    if schema and compiler:
        for filename, owners in registrations.items():
            path = root / 'Civ Supply Chains' / filename
            if path.suffix.lower() != '.sql' or not path.is_file():
                continue
            for action, index, offset in owners:
                if action['type'] != 'UpdateDatabase':
                    continue
                text = path.read_text(encoding='utf-8-sig')
                if not any(write_table(tokens) in declarations for tokens in statements(text)):
                    continue
                try:
                    position = (int(action.get('properties', {}).get('LoadOrder')), index, offset)
                except (TypeError, ValueError):
                    errors.append(f'{filename}: declaration input needs a numeric LoadOrder')
                    continue
                if not schema < position < compiler:
                    errors.append(f'{filename}: declarations must load after Schema and before the transaction compiler')
    return errors
