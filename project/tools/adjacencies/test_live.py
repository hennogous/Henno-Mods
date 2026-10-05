"""Verify actual native yields and UI output in a disposable CSC-only game.

Mutates a fresh turn-1 fixture. Never run against a campaign; requires the
explicit flag below. The tuner must expose CSC_AdjacencyGameplay and PlotInfo.
"""
import argparse
import json
import time
from pathlib import Path
import tuner

ROOT=Path(__file__).resolve().parents[3]
TESTS=ROOT/'project/tests/adjacencies'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disposable-turn-1-game',action='store_true',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--port',type=int,default=4318)
    args=parser.parse_args()
    tuner.PORT=args.port
    args.output.mkdir(parents=True,exist_ok=True)
    states=tuner.states()
    gameplay=states['CSC_AdjacencyGameplay']; ui=states['PlotInfo']
    log=[]
    def run(name,code,state=gameplay):
        messages=tuner.command(code+'\nprint("CSC_LIVE_STEP_PASS","'+name+'")',state,1.5)
        text='\n'.join(messages); log.append(name+'\n'+text)
        (args.output/'live-verification.txt').write_text('\n\n'.join(log),encoding='utf-8')
        if 'ERR:' in text or 'CSC_LIVE_STEP_PASS\t'+name not in text:
            raise AssertionError(name+' failed: '+text)
        print('PASS: '+name,flush=True)
    run('fresh fixture',(TESTS/'live_fixture.lua').read_text(encoding='utf-8'))
    run('prepare transitions',(TESTS/'live_transitions.lua').read_text(encoding='utf-8'))
    def yields(name):
        run(name+' zero bits','CSC_LiveZeroBits()')
        run(name+' baseline','CSC_LiveCaptureBaseline(); CSC_RefreshAdjacencies()')
        run(name+' native yield delta','CSC_LiveAssertYields("'+name+'")')
    yields('materials and customers')
    run('ownership removal','CSC_LiveRemoveMaterialOwner()')
    yields('material ownership removed')
    run('empire mill gate','CSC_LiveEnableRemoteMill()')
    yields('remote mill')
    run('remove empire mill','CSC_LiveRemoveRemoteMill()')
    yields('mill removed')
    run('55 native source evaluators','CSC_LiveAssertSources()')
    run('native placement preview and tooltip',(TESTS/'live_ui.lua').read_text(encoding='utf-8'),ui)
    report={'status':'passed','ruleCount':26,'sourceCount':55,
            'checks':['native yield deltas against cleared-bit baseline','BASE/SPEC material counts',
                      'customer return yields','material ownership removal','empire-wide mill gate',
                      'mill removal clears bits','55 source evaluators in gameplay context',
                      'native placement preview','district tooltip dispatcher','edge face deduplication'],
            'limitations':['visual appearance requires human review','optional mods tested in frozen SQL fixture, not live here',
                           'save/reload and MAB coexistence are separate release checks']}
    (args.output/'live-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: live gameplay and UI checks',flush=True)


if __name__=='__main__': main()
