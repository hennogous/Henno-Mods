"""Retain the sole Frida session until exact held native exit; never detach."""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'project/tools/ai_baseline'),str(Path(__file__).parent)]
from full_game_controller.windows_process import HeldProcess
from observer_host import write,validate_contract,validate_status,expected_hook_count


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--dependencies',type=Path,required=True);args=parser.parse_args()
    out=args.output;session=None;script=None;held=None
    try:
        expected=json.loads((out/'native-owner.json').read_text());held=HeldProcess(expected['pid'])
        if held.identity!=expected or held.poll()is not None:raise RuntimeError('Exact native identity mismatch')
        spec=json.loads((out/'native-spec.json').read_text());config=json.loads((out/'observer-config.json').read_text());validate_contract(spec,config,expected_hook_count(config))
        proof=json.loads((out/'loaded-module.json').read_text())
        if proof.get('identity')!=expected or not proof.get('verified'):raise RuntimeError('Loaded-module owner proof missing')
        if hashlib.sha256(Path(spec['path']).read_bytes()).hexdigest()!=spec['sha256']:raise RuntimeError('Native file hash changed')
        sys.path.insert(0,str(args.dependencies));import frida
        if frida.__version__!='17.24.3':raise RuntimeError('Require the native-exercised Frida17.24.3')
        source=(out/'trace.js').read_text(encoding='utf-8-sig')
        if source.count('__SPEC__')!=1 or source.count('__CONFIG__')!=1:raise ValueError('Explicit observer template contract missing')
        session=frida.attach(expected['pid'])
        def detached(*details):
            receipt={'identity':expected,'time':time.time(),'details':str(details),'native_alive':held.poll()is None}
            with(out/'detachments.ndjson').open('a')as stream:stream.write(json.dumps(receipt)+'\n');stream.flush();os.fsync(stream.fileno())
            write(out/'detachment.json',receipt)
        session.on('detached',detached)
        script=session.create_script(source.replace('__SPEC__',json.dumps(spec)).replace('__CONFIG__',json.dumps(config)))
        def received(message,data):
            write(out/'trace-message.json',message)
            if message.get('type')=='error':write(out/'trace-daemon-error.json',{'message':message,'retain_until_native_exit':True})
        script.on('message',received);script.load();status=script.exports_sync.status();validate_status(status,spec,enabled=False,config=config)
        write(out/'trace-ready.json',{'identity':expected,'daemon_pid':os.getpid(),'frida_version':frida.__version__,'status':status,'time':time.time()})
        started=False;frozen=False
        while held.poll()is None:
            if(out/'trace-start.request').exists()and not started:
                started=True;value=script.exports_sync.start();write(out/'trace-started.json',{'result':value,'status':script.exports_sync.status()})
            request=out/'trace-snapshot.request'
            if request.exists()and not frozen:
                token=request.read_text();write(out/('trace-snapshot-'+token+'.json'),script.exports_sync.snapshot());request.unlink()
            if(out/'trace-freeze.request').exists()and not frozen:
                frozen=True;value=script.exports_sync.freeze();write(out/'trace-counts.json',{'snapshot':value,'status':script.exports_sync.status()})
            time.sleep(.2)
    except BaseException:
        write(out/'trace-daemon-error.json',{'traceback':traceback.format_exc(),'retain_until_native_exit':True})
    finally:
        # Keep Frida session/script references alive. No unload/detach, including
        # runner exceptions and missing RPC acknowledgements while native lives.
        while held and held.poll()is None:time.sleep(.5)
        identity=held.identity if held else None
        if held:held.close()
        write(out/'trace-daemon-exit.json',{'identity':identity,'native_absent':held is not None,'explicit_detach':False,'time':time.time()})


if __name__=='__main__':main()
