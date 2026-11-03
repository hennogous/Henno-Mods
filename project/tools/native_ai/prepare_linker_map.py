"""Index an MSVC linker map and check its layout against a local PE. No execution."""
import argparse, csv, hashlib, json, re, struct
from pathlib import Path

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def pe_info(path):
    data = Path(path).read_bytes()
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    assert data[pe:pe+4] == b'PE\0\0'
    machine, count, timestamp = struct.unpack_from('<HHI', data, pe+4)
    optsize = struct.unpack_from('<H', data, pe+20)[0]
    opt = pe+24
    assert machine == 0x8664 and struct.unpack_from('<H', data, opt)[0] == 0x20b
    base = struct.unpack_from('<Q', data, opt+24)[0]
    sections = []
    for i in range(count):
        p = opt+optsize+40*i
        name = data[p:p+8].rstrip(b'\0').decode('ascii')
        size, rva, rawsize, raw = struct.unpack_from('<IIII', data, p+8)
        sections.append(dict(name=name, size=size, rva=rva, rawsize=rawsize, raw=raw))
    def offset(rva):
        for s in sections:
            if s['rva'] <= rva < s['rva']+s['rawsize']:
                return s['raw']+rva-s['rva']
        raise ValueError(hex(rva))
    pdata, length = struct.unpack_from('<II', data, opt+112+3*8)
    starts = set()
    for p in range(offset(pdata), offset(pdata)+length, 12):
        start, end, unwind = struct.unpack_from('<III', data, p)
        if start: starts.add(start)
    return dict(sha256=sha(path), timestamp=hex(timestamp), image_base=base,
                entry=struct.unpack_from('<I', data, opt+16)[0], sections=sections), starts

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--map', required=True); ap.add_argument('--binary', required=True); ap.add_argument('--output', required=True)
    args=ap.parse_args(); out=Path(args.output); out.mkdir(parents=True, exist_ok=True)
    info, starts=pe_info(args.binary)
    rows=[]; absolute=0; synthetic=0; segment_bases={}; scope='public'
    text=Path(args.map).read_text(encoding='utf-8',errors='replace')
    base=int(re.search(r'Preferred load address is ([0-9a-fA-F]+)',text)[1],16)
    timestamp=re.search(r'Timestamp is ([0-9a-fA-F]+)',text)[1]
    pattern=re.compile(r'^\s*([0-9A-Fa-f]{4}):([0-9A-Fa-f]{8})\s+(\S+)\s+([0-9A-Fa-f]{16})\s+(.*)$')
    for line in text.splitlines():
        if line.strip()=='Static symbols': scope='static'
        m=pattern.match(line)
        if not m: continue
        seg, off, name, va, rest=m.groups(); seg=int(seg,16); off=int(off,16); va=int(va,16)
        if seg==0: absolute+=1; continue
        rva=va-base; flags=rest.split(); function='f' in flags[:-1]
        # MSVC import-section sentinels wrap their section offset and point at image base.
        if name=='.idata$6' and rva==0 and off>=0x80000000:
            synthetic+=1; continue
        segment_bases.setdefault(seg,set()).add(rva-off)
        rows.append((hex(rva), 'function' if function else 'data', scope, name, flags[-1], 'yes' if rva in starts else 'no'))
    with (out/'symbols.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['rva','kind','scope','mangled','object','pdata_start']); w.writerows(rows)
    funcs={int(r[0],16) for r in rows if r[1]=='function'}
    map_entry=re.search(r'entry point at\s+([0-9a-fA-F]+):([0-9a-fA-F]+)',text)
    entry=next(iter(segment_bases[int(map_entry[1],16)]))+int(map_entry[2],16)
    layout={str(k):[hex(v) for v in sorted(values)] for k,values in segment_bases.items()}
    agreement=all(len(v)==1 and next(iter(v))==info['sections'][k-1]['rva'] for k,v in segment_bases.items())
    report=dict(map_path=str(Path(args.map).resolve()), binary_path=str(Path(args.binary).resolve()), map_sha256=sha(args.map), pe=info,
        map_timestamp='0x'+timestamp,map_timestamp_equal=('0x'+timestamp==info['timestamp']),
        image_base_equal=base==info['image_base'], segment_bases=layout, segment_layout_equal=agreement,
        entry_equal=entry==info['entry'], map_entry=hex(entry), rows=len(rows), absolute_skipped=absolute, synthetic_import_sentinels_skipped=synthetic,
        function_rows=sum(r[1]=='function' for r in rows), unique_function_addresses=len(funcs),
        function_addresses_at_pdata_starts=len(funcs&starts), pdata_starts=len(starts),
        warning='Layout agreement supports address use, not exact build identity. Timestamp mismatch retained. Leaf functions need not have pdata entries. No size/signature inferred from adjacent symbols.')
    (out/'map-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
