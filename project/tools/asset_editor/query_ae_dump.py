"""Read captured native memory/disassembly offline; no process interaction."""
import argparse,bisect,mmap,struct,sys
from pathlib import Path

class Dump:
    def __init__(self,path):
        self.file=Path(path).open('rb');self.data=mmap.mmap(self.file.fileno(),0,access=mmap.ACCESS_READ)
        if self.data[:4]!=b'MDMP': raise ValueError('Not a Windows dump')
        n,r=struct.unpack_from('<II',self.data,8)
        self.streams={struct.unpack_from('<III',self.data,r+i*12)[0]:struct.unpack_from('<III',self.data,r+i*12)[1:] for i in range(n)}
        o=self.streams[9][1];count,pos=struct.unpack_from('<QQ',self.data,o);self.ranges=[]
        for i in range(count):
            start,size=struct.unpack_from('<QQ',self.data,o+16+i*16);self.ranges.append((start,start+size,pos));pos+=size
        self.starts=[x[0] for x in self.ranges];self.modules=[]
        o=self.streams[4][1]
        for i in range(struct.unpack_from('<I',self.data,o)[0]):
            b,z,cs,ts,nam=struct.unpack_from('<QIIII',self.data,o+4+i*108)
            ln=struct.unpack_from('<I',self.data,nam)[0];name=self.data[nam+4:nam+4+ln].decode('utf-16le')
            self.modules.append((b,b+z,name))
    def read(self,address,size):
        i=bisect.bisect_right(self.starts,address)-1
        if i<0: raise ValueError('Unmapped address '+hex(address))
        b,e,p=self.ranges[i]
        if not b<=address<e or address+size>e: raise ValueError('Unmapped range '+hex(address))
        return self.data[p+address-b:p+address-b+size]
    def q(self,address): return struct.unpack('<Q',self.read(address,8))[0]
    def describe(self,address):
        for b,e,name in self.modules:
            if b<=address<e:return Path(name).name+'+'+hex(address-b)
        try:
            raw=self.read(address,min(128,self.ranges[bisect.bisect_right(self.starts,address)-1][1]-address))
            s=raw.split(b'\0',1)[0]
            if len(s)>2 and all(32<=c<127 for c in s): return repr(s.decode())
        except ValueError: pass
        return ''
    def close(self): self.data.close();self.file.close()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('dump');ap.add_argument('address',type=lambda v:int(v,0));ap.add_argument('--size',type=lambda v:int(v,0),default=256);ap.add_argument('--disassemble',action='store_true');ap.add_argument('--capstone-dir');a=ap.parse_args()
    d=Dump(a.dump)
    try:
        if a.disassemble:
            if a.capstone_dir:sys.path.insert(0,a.capstone_dir)
            from capstone import Cs,CS_ARCH_X86,CS_MODE_64
            for ins in Cs(CS_ARCH_X86,CS_MODE_64).disasm(d.read(a.address,a.size),a.address):print(hex(ins.address),ins.mnemonic,ins.op_str)
        else:
            for address in range(a.address,a.address+a.size,8):
                value=d.q(address);print(hex(address),hex(value),d.describe(value))
    finally:d.close()
