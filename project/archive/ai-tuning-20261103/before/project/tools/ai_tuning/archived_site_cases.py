"""Read-only adapter for three pinned archived partial observations, never policy input."""
import hashlib
import json
from pathlib import Path
import sqlite3
from site_evaluator import evaluate_site

DEFAULT_ARCHIVE = Path(r'C:/Users/Shadow/Desktop/Codex/csc-rh5-parity-campaign-20261024/basic-A/run-01')
PINS = {
    'game-01/turn-100.json': '01c79c4d94c81e7d4abd0d161e7cfa2dd5f6c5194e0a59086b029b978c0547c5',
    'native-gameplay.sqlite': 'f5853322b13fa5bdd7c2d803dea859f7e3912de453bd65cce8e0c92a580a6946',
    'source-version/0022-paired_observer.lua': '3817842502b0618c80539714e7b83937505f164b43306b402b2b3c8e33a7e79c',
}


def archived_cases(root=DEFAULT_ARCHIVE):
    root = Path(root)
    sources = {}
    for relative, expected in PINS.items():
        path = root / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Archive pin mismatch: ' + str(path))
        sources[relative] = {'path': str(path), 'sha256': actual}
    snap = json.loads((root / 'game-01/turn-100.json').read_text(encoding='utf-8'))
    def src(pointer):
        return str(root / 'game-01/turn-100.json') + ' SHA256 ' + PINS['game-01/turn-100.json'] + ' #' + pointer
    def fact(value, pointer):
        return {'value': value, 'source': src(pointer)}
    database = root / 'native-gameplay.sqlite'
    dbsrc = str(database) + ' SHA256 ' + PINS['native-gameplay.sqlite']
    # Read only by URI; never use rowid as a game index.
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as db:
        config = db.execute('SELECT QuarterKey,SourceTag FROM CSC_QuarterMaterialAdjacencyConfig').fetchall()
        classes = {}
        for quarter in ('BAKERS', 'TAILORS'):
            classes[quarter] = {}
            for role, suffix in (('base', '_BASE'), ('specialty', '_SPEC')):
                tags = [tag for q, tag in config if q == quarter and tag.endswith(suffix)]
                if len(tags) != 1:
                    raise ValueError('Ambiguous archived Quarter mapping')
                classes[quarter][role] = tags[0]
        tags = [{'Type': t, 'Tag': tag, 'source': dbsrc + ' TypeTags ' + repr((t, tag))}
                for t, tag in db.execute('SELECT Type,Tag FROM TypeTags')
                if tag in {v for roles in classes.values() for v in roles.values()}]
        resources = {r['Type'] for r in tags}
        valid = [{'ResourceType': r, 'ImprovementType': i,
                  'source': dbsrc + ' Improvement_ValidResources ' + repr((r, i))}
                 for r, i in db.execute('SELECT ResourceType,ImprovementType FROM Improvement_ValidResources')
                 if r in resources]
    mapping = {'snapshot': dbsrc, 'validated': {'value': True, 'source': dbsrc + ' explicit config/TypeTags/Improvement_ValidResources extraction'},
               'quarter_classes': classes, 'TypeTags': tags, 'Improvement_ValidResources': valid}
    cases = []
    for ci, di in ((3, 2), (16, 1)):
        city = snap['cities'][ci]; district = city['districts'][di]
        pointer = f'/cities/{ci}/districts/{di}'
        site = {'identity': {'player': city['player'], 'city': city['id'], 'turn': snap['turn'],
                            'plot': district['plot'], 'source': src(pointer)},
                'source_kind': 'observed_existing', 'quarter': district['quarter'],
                'current_real': {}, 'materials': [], 'future': [],
                'river': fact(district['site']['river'], pointer + '/site/river'),
                'current_customers': fact(district['site']['sales_plots'], pointer + '/site/sales_plots'),
                'built_stages': fact([b for b in city['buildings'] if b['plot'] == district['plot']], f'/cities/{ci}/buildings'),
                'build_commitment': fact({'complete': district['complete'], 'pillaged': district['pillaged']}, pointer),
                'observed_district_yields': fact(district['yields'], pointer + '/yields')}
        for mi, material in enumerate(district['site']['materials']):
            mp = pointer + f'/site/materials/{mi}'
            site['materials'].append({**material, 'source': src(mp), 'adjacent': fact(True, mp),
                'improved_working': fact(bool(material.get('improvement')) and not material['pillaged'], mp)})
        cases.append({'id': f'existing-{district["plot"]}', 'ai_recommendation_eligible': True,
                      'purpose': 'Existing AI chain observation; not a new-placement recommendation',
                      'site': site, 'result': evaluate_site(site, mapping)})
    option = snap['options'][0]; observed = option['sites'][0]
    human = next(p['human'] for p in snap['players'] if p['id'] == option['player'])
    if human is not True or observed['plot'] != 2934:
        raise ValueError('Negative control identity changed')
    pointer = '/options/0/sites/0'
    occupied = snap['plots'][735]
    if occupied.get('district') != 'DISTRICT_CITY_CENTER' or occupied['index'] != 2860:
        raise ValueError('Negative occupancy control changed')
    site = {'identity': {'player': option['player'], 'city': option['city'], 'turn': snap['turn'],
                        'plot': observed['plot'], 'source': src(pointer)},
            'source_kind': 'observed_human_candidate_negative_control', 'quarter': option['quarter'],
            'legal': fact(True, pointer + ' observer B.options CanHaveDistrict filter'),
            'river': fact(observed['river'], pointer + '/river'), 'current_real': {},
            'materials': [{**observed['materials'][0], 'source': src(pointer + '/materials/0'),
                           'adjacent': fact(True, pointer + '/materials/0'),
                           'improved_working': fact(False, '/plots/735')}],
            'future': [{'plot': 2860, 'kind': 'material', 'resource': 'RESOURCE_CSC_FLAX',
                        'improvement': 'IMPROVEMENT_FARM', 'source': src('/plots/735') + ' deliberately invalid Farm proposal',
                        'legal': fact(False, '/plots/735 City Center occupancy'),
                        'adjacent': fact(True, pointer + '/materials/0')}]}
    cases.append({'id': 'human-2934-occupied-material-control', 'ai_recommendation_eligible': False,
                  'purpose': 'Original human player; excluded from AI recommendations; invalid Farm occupancy control',
                  'site': site, 'result': evaluate_site(site, mapping)})
    return {'source_files': sources, 'mapping': mapping, 'partial_cases': cases,
            'counts': {'partial_evaluated': 3, 'ai_existing_chains': 2, 'original_human_excluded': 1,
                       'complete_sites': 0, 'ranked_sites': 0},
            'limits': ['District GetYield totals are retained separately, never candidate real adjacency.',
                       'Owned mapped unpillaged improvements do not establish full native bound supply eligibility.',
                       'Foundation gates/costs, complete material inventory, alternatives and future returns/delays remain unknown.',
                       'Existing districts do not establish current new-placement legality.']}


if __name__ == '__main__':
    print(json.dumps(archived_cases(), indent=2))
