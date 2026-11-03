"""One-shot diagnostic attachment of a preexisting shipped native rule."""
from pathlib import Path
from service_planner.native_adapter import parse

DEFINITION='TRAIT_MAORI_PREVENT_HARVEST'
def verify_live(value,turn=16,*,confirmed=False):
    assert value['turn']==turn and value['active']is False and value['definition']==DEFINITION,'Rule phase/definition changed'
    assert value.get('ui_turn',turn)in(turn,turn-1),'Unexpected UI/Core phase'
    rows=value['instances'];assert len(rows)==5,'Exactly five live instances required'
    assert {x['player']for x in rows}==set(range(1,6))and len({x['runtime_id']for x in rows})==5,'Wrong or duplicate native rule owner'
    assert all(x['active']is True for x in rows),'Native rule inactive'
    ledger=value['ledger'];assert ledger['attempted']==ledger['returned']==[1,2,3,4,5],'Partial rule attempt'
    assert ledger['status']==('confirmed'if confirmed else'returned'),'Rule ledger not closed'
    return True

def activate(r,root,write,lua,*,token='native-harvest-live-v4',turn=16):
    root=Path(root);r.cmd(Path(__file__).with_name('native_harvest_rule_ui.lua').read_text(encoding='utf-8'),'PlotInfo','install-native-harvest-runtime-UI-reader')
    r.cmd(Path(__file__).with_suffix('.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','install-native-harvest-rule-reader')
    request=dict(enabled=True,token=token,turn=turn)
    before=parse(r.cmd('CSC_NATIVE_HARVEST_RULE.Read('+lua(request)+');','CSC_AdjacencyGameplay','native-harvest-before-readonly'),'CSC_NATIVE_RULE')
    write(root/'native-rule-before.json',before)
    assert before['turn']==turn and not before['active']and not before['instances']and before.get('ledger')is None,'Unreconciled prior rule effects'
    # Shared command journal is fsynced before this one send. No attachment retry.
    returned=parse(r.cmd('CSC_NATIVE_HARVEST_RULE.Begin('+lua(request)+');','CSC_AdjacencyGameplay','native-harvest-attach-once'),'CSC_NATIVE_RULE')
    write(root/'native-rule-attach-returned.json',returned)
    samples=[]
    for i in range(3):
        value=parse(r.cmd('CSC_NATIVE_HARVEST_RULE.Read('+lua(request)+');','CSC_AdjacencyGameplay','native-harvest-active-readonly-'+str(i)),'CSC_NATIVE_RULE');samples.append(value)
    write(root/'native-rule-readbacks.json',samples)
    for sample in samples:verify_live(sample,turn)
    assert all(x['instances']==samples[0]['instances']for x in samples),'Runtime instance identities changed'
    closed=parse(r.cmd('CSC_NATIVE_HARVEST_RULE.Confirm('+lua(request)+');','CSC_AdjacencyGameplay','native-harvest-confirm-ledger-once'),'CSC_NATIVE_RULE');verify_live(closed,turn,confirmed=True)
    write(root/'native-rule-confirmed.json',closed)
    return dict(verified_active_runtime_rule=True,definition=DEFINITION,players=[1,2,3,4,5],observer0_excluded=True,attachment_commands=1,per_player_attachment_attempts=5,runtime_instances=closed['instances'],direct_unit_orders=0,economic_grants=0,native_harvest_prevention_behavior_proven=False)
