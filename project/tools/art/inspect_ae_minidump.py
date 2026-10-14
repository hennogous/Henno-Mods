"""Print an x64 dump's fault and raw stack candidates, not a symbolic backtrace.

Memory mapping supports multi-GB full dumps without reading them all into RAM.
"""
import mmap, struct, sys
from pathlib import Path
source=Path(sys.argv[1]).open('rb')
d=mmap.mmap(source.fileno(),0,access=mmap.ACCESS_READ)
if d[:4]!=b'MDMP': raise SystemExit('Not a Windows minidump.')
def u(fmt,offset): return struct.unpack_from('<'+fmt,d,offset)
n,r=u('II',8)
streams={u('III',r+i*12)[0]:u('III',r+i*12)[1:] for i in range(n)}
if not {3,4,6,7}.issubset(streams): raise SystemExit('Required dump streams are missing.')
if u('H',streams[7][1])[0]!=9: raise SystemExit('This reader supports x64 dumps only.')
o=streams[6][1]
print('exception',u('IIQQ',o+8))
cr,ca=u('II',o+160)
print('rsp/rip',*[hex(u('Q',ca+x)[0]) for x in [152,248]])
p=streams[4][1];mods=[]
for i in range(u('I',p)[0]):
 q=p+4+i*108
 b,sz,cs,ts,nam=u('QIIII',q)
 ln=u('I',nam)[0]
 name=d[nam+4:nam+4+ln].decode('utf-16le')
 mods.append((b,sz,name))
p=streams[3][1];tid=u('I',o)[0]
for i in range(u('I',p)[0]):
 q=p+4+i*48
 if u('I',q)[0]!=tid: continue
 st,sz,rv=u('QII',q+24)
 print('stack',hex(st),sz)
 # The confirmed texture failure's useful frames were beyond the first 2 KiB.
 for j in range(min(sz,65536)//8):
  a=u('Q',rv+j*8)[0]
  for b,z,name in mods:
   if b<=a<b+z: print(j*8,hex(a),name,hex(a-b))
d.close()
source.close()
