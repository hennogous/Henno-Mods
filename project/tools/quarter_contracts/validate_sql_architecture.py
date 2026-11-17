#!/usr/bin/env python3
"""Check current SQL architecture and wiring independently of design approvals."""
import argparse
import json

import yaml
from sql_architecture import ROOT, load_contract, validate_core, validate_pipeline
from validate_phase import validate_action_wiring, validate_content_wiring


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('quarter', nargs='?', default='tailors')
    args = parser.parse_args()
    implementation = yaml.safe_load((ROOT/f'project/specs/{args.quarter}/implementation.yaml').read_text(encoding='utf-8'))
    shared = load_contract(ROOT, implementation['shared_sql_contract'])
    wiring = implementation['build_wiring']
    manifest = json.loads((ROOT/wiring['action_manifest']).read_text(encoding='utf-8'))
    errors = validate_pipeline(ROOT, shared, manifest)
    errors.extend(validate_core(ROOT/implementation['planned_outputs']['core'], shared))
    outputs = set(wiring['actions']) | set(wiring.get('content_only', {}))
    errors.extend(validate_action_wiring(manifest, wiring, outputs))
    errors.extend(validate_content_wiring(ROOT/wiring['source_project'], wiring, outputs))
    for error in errors:
        print('ERROR: ' + error)
    if errors:
        return 1
    print(f'PASS: {args.quarter} SQL ownership, shared pipeline and registered file contracts')
    # This focused maintenance check does not advance control.yaml gates or
    # refresh canonical design hashes. Phase acceptance keeps its own checks.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
