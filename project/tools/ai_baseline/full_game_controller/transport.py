"""One-send FireTuner transaction with bounded ACK reception on the SAME socket.

Connect failures may retry before transmission. No reconnect after transmission,
discovery, launch or resend logic. Partial frames survive receive timeouts.
"""
import re,socket,struct,time

class MissingAcknowledgment(RuntimeError):
 def __init__(self,label,text):
  self.label=label;self.text=text;self.sent_once=True
  super().__init__(label+': command sent once; acknowledgment not received within bound')

class NativeLuaFailure(RuntimeError):
 def __init__(self,text):
  self.text=text;self.sent_once=True
  super().__init__('Native Lua failure: '+text[-3000:])

def receive_command(lua,state,token,port,timeout=15,check=True,connect=None,clock=None,sleep=None):
 connect=connect or socket.create_connection;clock=clock or time.monotonic;sleep=sleep or time.sleep
 wrapped='local ok,e=pcall(function()\n'+lua+'\nend);print("'+token+'",ok,tostring(e));'
 payload=('CMD:'+str(state)+':'+wrapped).encode('utf-8')+b'\0'
 messages=[];pending=b'';deadline=clock()+timeout
 # A refused/timed-out connect has not obtained a socket or sent any command.
 # Retry only that setup step, bounded by three attempts and the same deadline.
 # Once sendall is attempted, every failure is ambiguous: never reconnect/send.
 for attempt in range(3):
  try:
   connection=connect(('127.0.0.1',port),timeout=min(5,max(.01,deadline-clock())))
   break
  except(ConnectionRefusedError,socket.timeout):
   if attempt==2 or clock()>=deadline:raise
   sleep(min(.25,max(0,deadline-clock())))
 with connection as sock:
  sock.settimeout(5);sock.sendall(struct.pack('<II',len(payload),1)+payload)
  while clock()<deadline:
   sock.settimeout(min(0.5,max(0.01,deadline-clock())))
   try:chunk=sock.recv(65536)
   except socket.timeout:continue
   if not chunk:break
   pending+=chunk
   while len(pending)>=8:
    length,sender=struct.unpack('<II',pending[:8]);assert length<=16*1024*1024,'Invalid native frame size'
    if len(pending)<8+length:break
    frame=pending[8:8+length];pending=pending[8+length:]
    encoding='utf-16le'if frame.count(b'\0')>len(frame)*0.3 else'utf-8'
    messages.append(frame.decode(encoding,errors='replace').strip('\x00'))
   text='\n'.join(messages)
   match=re.search(re.escape(token)+r'\s+(true|false)(?:\s+([^\r\n]*))?',text)
   if match:
    if match[1]=='false':raise NativeLuaFailure(text)
    return text,True
 text='\n'.join(messages)
 if check:raise MissingAcknowledgment(token,text)
 return text,False
