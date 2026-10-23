"""Bounded retries for explicitly read-only FireTuner calls; never resend mutations."""
import re,time

class IncompleteTunerRead(RuntimeError):
 pass

def transient_read_error(error):
 if isinstance(error,(OSError,EOFError,KeyError,IncompleteTunerRead)):return True
 if not isinstance(error,RuntimeError):return False
 text=str(error)
 # An actual Lua failure is meaningful evidence, not a transport timeout.
 if re.search(r'CSCBASE_OK_\d+\s+false\b',text) or 'stack traceback:' in text or 'ERR:' in text:return False
 return ' failed: ' in text or text=='No responsive tuner states'

def retry_read(operation,on_retry=lambda attempt,error,delay:None,*,attempts=6,budget=120,sleep=time.sleep,clock=time.monotonic):
 start=clock()
 for attempt in range(1,attempts+1):
  try:return operation(attempt)
  except Exception as error:
   delay=min(2**attempt,12)
   if not transient_read_error(error) or attempt>=attempts or clock()-start+delay>=budget:raise
   on_retry(attempt,error,delay);sleep(delay)
