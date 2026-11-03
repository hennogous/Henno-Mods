"""Owned disposable native-host verification; never attaches to Civ."""
import argparse,json,pathlib,subprocess,sys,threading
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def main():
 p=argparse.ArgumentParser();p.add_argument('--dependencies',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
 if a.output.exists(): raise ValueError('Fresh receipt path required')
 sys.path.insert(0,str(a.dependencies));import frida
 assert frida.__version__=='17.24.3'
 proc=subprocess.Popen([sys.executable,'-B','-c','input()'],stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 timer=threading.Timer(45,lambda:proc.terminate() if proc.poll() is None else None);timer.start()
 session=script=None;messages=[]
 try:
  target=ROOT/'project/tools/native_ai/quarter_placement_trial/synthetic_target.c'
  source=(HERE/'synthetic.js').read_text().replace('__KERNEL_C__',json.dumps((HERE/'kernel.c').read_text())).replace('__TARGET_C__',json.dumps(target.read_text()))
  session=frida.attach(proc.pid);script=session.create_script(source);script.on('message',lambda m,d:messages.append(m));script.load()
  result=script.exports_sync.exercise();result['messages']=messages
  assert result['passed'] and not messages,result
  proc.stdin.write(b'\n');proc.stdin.flush();proc.wait(timeout=10);assert proc.returncode==0
  result['native_exit_code']=proc.returncode;a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(result['checks']),exit_code=proc.returncode)))
 finally:
  if proc.poll() is None:proc.stdin.write(b'\n');proc.stdin.flush();proc.wait(timeout=10)
  timer.cancel()
if __name__=='__main__':main()
