"""Create the human-readable report from completed read-only Blender audit rows."""
import csv
from html import escape
import json
from pathlib import Path
import sys

output = Path(sys.argv[1])
records = {}
for line in (output / 'files.jsonl').read_text(encoding='utf-8').splitlines():
    row = json.loads(line)
    if row.get('audit_version') == 2:
        records[row['path']] = row
inventory = json.loads((output / 'inventory.json').read_text(encoding='utf-8'))
assert len(records) == len(inventory), 'Audit incomplete'
rows = list(records.values())
assert all(row['source_unchanged'] for row in rows), 'A source changed during the audit'
assert not any(row.get('error') or row.get('measurement_error') for row in rows), 'Audit has unresolved errors'
candidates = sorted((row for row in rows if row['candidate_packed_bytes']),
                    key=lambda row: row['measured_candidate_saving'], reverse=True)
groups = []
for backups in (False, True):
    selected = [row for row in rows if row['backup'] == backups]
    groups.append({'kind': 'Blender backups (.blend1)' if backups else 'Regular .blend files (including archived versions)',
                   'files': len(selected), 'affected': sum(bool(row['candidate_packed_bytes']) for row in selected),
                   'current_bytes': sum(row['file_bytes'] for row in selected),
                   'saving_bytes': sum(row['measured_candidate_saving'] for row in selected),
                   'unreferenced_saving_bytes': sum(row['measured_unreferenced_saving'] for row in selected)})
summary = {'scanned': len(rows), 'affected': len(candidates), 'all_sources_unchanged': True,
           'current_bytes': sum(row['file_bytes'] for row in rows),
           'saving_bytes': sum(row['measured_candidate_saving'] for row in rows),
           'unreferenced_saving_bytes': sum(row['measured_unreferenced_saving'] for row in rows),
           'protected_other_use_bytes': sum(image['packed_bytes'] for row in rows for image in row['images']
                                             if image['category'] in {'other_render_or_reference_use', 'other_datablock_use'}),
           'groups': groups, 'candidates': candidates}
(output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
with (output / 'candidate-files.csv').open('w', newline='', encoding='utf-8-sig') as stream:
    columns = ['relative_path', 'backup', 'file_bytes', 'candidate_packed_bytes',
               'measured_candidate_saving', 'measured_unreferenced_saving', 'source_unchanged']
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(candidates)


def mib(value):
    return f'{value / 1024**2:,.2f} MiB'


html = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Working Files: packed texture storage audit</title>',
        '<style>body{font:15px/1.5 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#24313d;background:#f6f8fa}',
        'h1{font-size:28px}table{border-collapse:collapse;width:100%;background:white;margin:24px 0}th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #dde3e8;vertical-align:top}',
        'th{background:#e7eef4}.path{overflow-wrap:anywhere;max-width:650px}.amount{white-space:nowrap}details{margin-top:8px}small{color:#52606e}li{margin:4px 0}</style>',
        '<h1>Unused packed textures in Working Files</h1><p>26 October 2026 · Read-only audit of all .blend and numbered Blender backups.</p>',
        f'<p><strong>{len(rows)} files scanned; {len(candidates)} files contain candidates. Potential saving: {mib(summary["saving_bytes"])}.</strong><br>',
        f'Of this, {mib(summary["unreferenced_saving_bytes"])} is from images with no actual datablock users. All source hashes and timestamps were unchanged.</p>',
        '<p>Measurements compare matched temporary resaves using the source compression setting, removing only packed image payloads. '
        'This isolates texture savings from Blender version conversion, other unused data and geometry changes. No source file was saved or altered.</p>',
        '<p>Materials assigned to any object slot, hidden variants, every scene, material overrides, nested shader groups and Geometry Nodes material references are protected. '
        'World lighting and other image uses are retained. Mix branches are treated conservatively. '
        'The larger estimate also includes textures in disconnected nodes or unassigned materials, which may be authoring/export references and merit review before removal. '
        f'Other non-shader image references totaling {mib(summary["protected_other_use_bytes"])} are excluded.</p>',
        '<table><tr><th>Files</th><th>Scanned</th><th>Affected</th><th>Current size</th><th>Potential saving</th><th>Unreferenced portion</th></tr>']
for group in groups:
    html.append(f'<tr><td>{escape(group["kind"])}</td><td>{group["files"]}</td><td>{group["affected"]}</td>'
                f'<td class="amount">{mib(group["current_bytes"])}</td><td class="amount">{mib(group["saving_bytes"])}</td>'
                f'<td class="amount">{mib(group["unreferenced_saving_bytes"])}</td></tr>')
html.append('</table><h2>Candidate files, largest saving first</h2><table><tr><th>File and image details</th><th>Potential saving</th><th>Unreferenced portion</th></tr>')
for row in candidates:
    image_details = []
    for image in row['images']:
        if image['category'] not in {'unreferenced', 'disconnected_or_unassigned_material'}:
            continue
        material_names = ', '.join(ref['material'] for ref in image['materials'])
        description = 'No actual users' if image['category'] == 'unreferenced' else 'Disconnected / unassigned material'
        image_details.append(f'<li>{escape(image["name"])} — {mib(image["packed_bytes"])} — {description}'
                             f'{("; " + escape(material_names)) if material_names else ""}</li>')
    html.append(f'<tr><td class="path">{escape(row["relative_path"])}<details><summary>Image details</summary><ul>{"".join(image_details)}</ul></details></td>'
                f'<td class="amount">{mib(row["measured_candidate_saving"])}</td><td class="amount">{mib(row["measured_unreferenced_saving"])}</td></tr>')
html.append('</table><p><small>Raw records: files.jsonl. Full summary: summary.json. File list: candidate-files.csv. '
            '“Unreferenced” excludes fake users; it describes current model dependency, not whether an artist may want the stored image later.</small></p></html>')
(output / 'report.html').write_text(''.join(html), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k != 'candidates'}, indent=2))
