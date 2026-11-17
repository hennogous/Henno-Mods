"""Order CSC actions for review and merge compatible file-list actions.

Order is numeric LoadOrder, action type, then action ID; every order is explicit.
Only declarative database/text/icon/import/placeholder actions are coalesced.
Gameplay and UI contexts, replacements and their identities stay explicit.
All properties, criteria and additional action metadata must match exactly.
Files retain their sequence within each input action; dependency-sensitive
shared schema/common and generator sections are never alphabetised.
"""
from collections import defaultdict
import copy
import json

MERGEABLE = {'UpdateDatabase', 'UpdateText', 'UpdateIcons', 'ImportFiles', 'DoNothing'}
# Frontend configuration and icon definitions share the ordinary content phase.
# Pedia imports belong before UI contexts at 500, alongside other shared modules.
PREVIOUSLY_IMPLICIT = {'Settings': 100, 'Settings_Text': 100, 'UpdateIcons': 100, 'CSC_QuarterPedia': 490}
GROUP_NAMES={
    frozenset(('CSC_Q_BAKERS','CSC_Q_TAILORS')):'CSC_Q_ALL_Definitions',
    frozenset(('CSC_Q_BAKERS_GOLD','CSC_Q_TAILORS_GOLD','CSC_QUARTERS_PEDIA')):'CSC_CoreContent',
    frozenset(('CSC_Q_BAKERS_MC_MODE','CSC_Q_TAILORS_MC_MODE')):'CSC_Q_ALL_Monopolies',
    frozenset(('CSC_Q_BAKERS_MC_MODE_GOLD','CSC_Q_TAILORS_MC_MODE_GOLD')):'CSC_Q_ALL_Monopolies_Gold',
}


def order(action):
    """Require an explicit phase; equal phases sort by type, then identifier."""
    value = action['properties']['LoadOrder']
    return (int(value), action['type'].casefold(), action['id'].casefold())


def organize(actions):
    """Return ordered actions and an audit of groups whose contracts match.

    Additional properties and metadata participate in the comparison too. A
    future Context or criteria change therefore prevents accidental merging.
    Script/UI actions create runtime contexts and always retain their identity.
    """
    groups = defaultdict(list)
    singles = []
    actions = copy.deepcopy(actions)
    for action in actions:
        properties = action.setdefault('properties', {})
        if 'LoadOrder' not in properties:
            if action['id'] not in PREVIOUSLY_IMPLICIT:
                raise ValueError('Choose a load order for ' + action['id'])
            properties['LoadOrder'] = str(PREVIOUSLY_IMPLICIT[action['id']])

    for action in sorted(actions, key=order):
        if action['type'] not in MERGEABLE or not action.get('files'):
            singles.append(action)
            continue
        contract = {key: value for key, value in action.items() if key not in ('id', 'files')}
        groups[json.dumps(contract, sort_keys=True)].append(action)

    mergers = []
    for group in groups.values():
        if len(group) == 1:
            singles.extend(group)
            continue
        ids = frozenset(action['id'] for action in group)
        combined = copy.deepcopy(group[0])
        # Preserve each file list's internal order. Schema must precede Common,
        # and native compiler sections must retain their dependency sequence.
        combined['files'] = [file for action in group for file in action['files']]
        if ids in GROUP_NAMES:
            combined['id'] = GROUP_NAMES[ids]
        elif combined['type'] == 'DoNothing':
            combined['id'] = 'CSC_ParkedQuarters'
        elif combined['type'] == 'ImportFiles':
            combined['id'] = ('CSC_SharedModules' if combined['properties']['LoadOrder'] == '490'
                              else 'CSC_UI_Imports')
        elif ids == frozenset(('CSC_ALL_TEXT', 'CSC_RESOURCES_TEXT')):
            combined['id'] = 'CSC_CommonText'
        elif ids == frozenset(('CSC_BAKERS_TEXT', 'CSC_QUARTERS_TEXT')):
            combined['id'] = 'CSC_QuarterText'
        elif ids == frozenset(('CSC_UI_CITY_PANEL_TEXT', 'CSC_UI_Text')):
            combined['id'] = 'CSC_UI_Text'
        else:
            # New cohorts need deliberate names rather than misleading IDs
            # inherited from the first input or accidental output collisions.
            raise ValueError('Name the compatible action group: ' + str(sorted(ids)))
        singles.append(combined)
        mergers.append({'id': combined['id'], 'previous_ids': sorted(ids), 'files': combined['files']})

    if len({action['id'] for action in singles}) != len(singles):
        raise ValueError('Duplicate action ID after consolidation')
    return sorted(singles, key=order), mergers
