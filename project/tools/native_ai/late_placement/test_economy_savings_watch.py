"""Offline identity/lifecycle and synthetic native-register diagnostic checks.

These fixtures prove decoding and failure semantics, not the native ABI. The ABI
comes from the separately qualified AI-N114/116/117 evidence and needs live
receipts before the new long-run observer itself can be called runtime verified.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from economy_savings_watch import EconomySavingsWatch, specification


class EconomicGuards(unittest.TestCase):
    def test_rejects_wrong_whole_binary_before_layout_access(self):
        with self.assertRaisesRegex(ValueError, 'artifact identity'):
            specification(Path(__file__))

    def test_bad_map_player_window_inputs_do_not_load_frida(self):
        base=dict(directory='unused', binary='unused', output='unused', write=Mock(),
                  start=0, through=250, width=74, height=46)
        for delta in [dict(start=5, through=5), dict(through=301), dict(players=[1, 1]),
                      dict(players=[6]), dict(width=0), dict(height=257),
                      dict(districts=0), dict(districts=True), dict(districts=4097),dict(capture_placement=1)]:
            with self.subTest(delta=delta), patch('economy_savings_watch.dependencies') as deps:
                with self.assertRaises(ValueError):
                    EconomySavingsWatch(**dict(base, **delta))
                deps.assert_not_called()

    def test_loaded_module_mismatch_never_attaches(self):
        w=EconomySavingsWatch.__new__(EconomySavingsWatch)
        w.attached=None; w.spec=dict(path='C:/qualified.dll'); w.frida=Mock()
        owner=Mock(); owner.poll.return_value=None
        with self.assertRaisesRegex(ValueError, 'Loaded module differs'):
            w.attach(owner,{})
        w.frida.attach.assert_not_called()

    def test_never_detaches_live_owner(self):
        w=EconomySavingsWatch.__new__(EconomySavingsWatch)
        w.owner=Mock(); w.owner.poll.return_value=None; w.attached=Mock(); w.write=Mock()
        with self.assertRaisesRegex(RuntimeError, 'live owner'):
            w.after_exit()
        w.attached.detach.assert_not_called(); w.write.assert_not_called()

    def test_drains_persistent_sequence_and_rejects_gaps(self):
        # The managed Windows sandbox's redirected system TEMP is not writable;
        # keep this disposable journal inside the already-authorized workspace.
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            w=EconomySavingsWatch.__new__(EconomySavingsWatch)
            w.output=Path(tmp); w.write=Mock(); w.rows=0; w.last_sequence=0
            rpc=Mock(); w.script=SimpleNamespace(exports_sync=rpc)
            rpc.drain.return_value=dict(records=[dict(sequence=1,kind='accounts'),
                                                dict(sequence=2,kind='quote')], faults=[],stopReason=None)
            w.drain(); self.assertEqual(w.rows,2)
            rpc.drain.return_value=dict(records=[dict(sequence=4,kind='bad')], faults=[],stopReason=None)
            with self.assertRaisesRegex(RuntimeError, 'sequence gap'):
                w.drain()
            self.assertEqual(len((Path(tmp)/'economy-savings.ndjson').read_text().splitlines()),3)

    def test_freeze_waits_for_native_pairs_and_drains_once(self):
        w=EconomySavingsWatch.__new__(EconomySavingsWatch)
        w.output=Path('unused'); w.write=Mock(); w.frozen=None; w.drain=Mock()
        rpc=Mock(); rpc.freeze.side_effect=[dict(frozen=False,active=1),dict(frozen=True,active=0)]
        w.script=SimpleNamespace(exports_sync=rpc)
        with patch('economy_savings_watch.time.sleep'):
            w.freeze(); w.freeze()
        self.assertEqual(rpc.freeze.call_count,2); w.drain.assert_called_once()

    def test_partial_or_faulted_journal_is_not_qualified(self):
        w=EconomySavingsWatch.__new__(EconomySavingsWatch)
        good=dict(frozen=True,active=0,faults=[],stopReason=None)
        w.frozen=good; w.messages=[]; w.qualify()
        for delta in [dict(frozen=False),dict(active=1),dict(faults=['read failed']),
                      dict(stopReason='bound')]:
            w.frozen=dict(good,**delta)
            with self.assertRaisesRegex(RuntimeError,'faulted'):
                w.qualify()

    @unittest.skipUnless(shutil.which('node'),'Node required for synthetic Frida VM')
    def test_register_memory_pairing_and_fail_closed_vm(self):
        script=Path(__file__).with_name('economy_savings_watch.js')
        result=subprocess.run(['node','-e',VM_FIXTURE,str(script)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads(result.stdout)
        self.assertEqual(report['hooks'],19)
        self.assertEqual(report['debits'],1)
        self.assertEqual(report['placementHooks'],20)


VM_FIXTURE = r"""
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8');
function fixture(mismatch=false,invalidFunds=false,capturePlacement=false){
  const mem=new Map(), hooks=new Map(); let calls=0;
  class P {
    constructor(v){this.v=Number(v);} add(o){return new P(this.v+o);}
    toString(){return String(this.v);} toInt32(){return this.v|0;}
    isNull(){return this.v===0;} equals(p){return this.v===p.v;}
    readS32(){if(!mem.has(this.v))throw Error('Unmapped '+this.v);return mem.get(this.v)|0;}
    readU32(){return this.readS32()>>>0;}
    readU8(){return this.readS32()&255;}
    readS8(){const v=this.readS32()&255;return v>127?v-256:v;}
    readS16(){const v=this.readS32()&65535;return v>32767?v-65536:v;}
    compare(p){return this.v<p.v?-1:this.v===p.v?0:1;}
    readPointer(){return new P(this.readS32());}
    readByteArray(n){return new Uint8Array(n).fill(mismatch?1:0).buffer;}
  }
  const p=v=>new P(v), put=(v,o,n)=>mem.set(v+o,n);
  put(0,0x3c,0x100);put(0,0x108,1793649108);
  const context={rpc:{exports:{}},ptr:p,Process:{platform:'windows',arch:'x64',pointerSize:8,
    findRangeByAddress:()=>({base:p(0),size:0x1000000,protection:'rw-'}),
    getModuleByName:()=>({base:p(0),path:'pinned.dll',size:12976128})},Interceptor:{
      attach(a,f){calls++;hooks.set(a.v,f);return {detach(){throw Error('Must retain live hooks');}};},flush(){}
    }};
  vm.createContext(context);vm.runInContext(source,context);
  const points=vm.runInContext(capturePlacement?'({...ECONOMY_POINTS,...ECONOMY_GUARDS,...PLACEMENT_POINTS})':'({...ECONOMY_POINTS,...ECONOMY_GUARDS})',context);
  const spec={path:'pinned.dll',name:'GameCore_XP2_FinalRelease.dll',
    sha256:'092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f',
    timestamp:1793649108,imageSize:12976128,
    points:Object.fromEntries(Object.entries(points).map(([k,rva])=>[k,{rva,prefix:'00'.repeat(32)}]))};
  const cfg={start:0,through:250,players:[1,2,3,4,5],width:74,height:46,districts:40,maxRecords:20000,capturePlacement};
  const rpc=context.rpc.exports;
  if(mismatch){assert.throws(()=>rpc.init(spec,cfg),/Loaded entry differs/);assert.equal(calls,0);return;}
  assert.equal(rpc.init(spec,cfg).hooks,capturePlacement?20:19);rpc.start();rpc.window(200,205);
  const city=0x10000,xy=0x20000,frame=0x30000,stack=0x40000,
    funds=0x50000,game=0x60000,delta=0x70000,economic=0x80000,
    player=0x90000,treasury=0xa0000,weights=0xb0000;
  put(0,0xb8aa68,game);put(game,0xc0,203);
  put(city,0xd8,1);put(city,0xa8,524295);
  put(xy,0,31);put(xy,4,5);put(frame,0x38,31);put(frame,0x3c,5);
  put(stack,0xc0,economic);put(stack,0xd0,funds+8);put(stack,0xd8,funds);
  put(economic,0x98,player);put(economic,0x120,128000);put(economic,0x250,funds);
  put(economic,0x1e0,weights);put(economic,0x1f0,4);put(economic,0x1c8,9);
  put(player,0xd8,1);put(player,0x780,treasury);put(treasury,0xa8,130560);
  [19200,8000,6400,12000].forEach((v,i)=>put(funds,i*4,v));
  [3,4,1,1].forEach((v,i)=>put(weights,i*4,v));put(delta,0,-25600);
  const regs={rbp:p(city),r12:p(xy),rax:p(100),r14:p(city),r15:p(100),rdi:p(64),rsp:p(stack)};
  function fire(name,overrides={}){
    const fn=hooks.get(points[name]);assert.equal(typeof fn,'function');
    fn.call({context:{...regs,...overrides},threadId:7});
  }
  fire('cityQuote');fire('savings');
  if(invalidFunds){
    put(stack,0xd0,funds+12);fire('savings');
    const broken=rpc.drain();assert.equal(broken.faults.length,1);
    assert.match(broken.faults[0],/fund identity differs/);
    assert.equal(broken.records.length,2); // failure adds no fabricated zero funds
    fire('savings');assert.equal(rpc.drain().records.length,0);return;
  }
  put(funds,8,6399);put(funds,0,19201);fire('savings');
  put(funds,8,6400);put(funds,0,19199);fire('savings');
  put(city,0xd8,6);fire('savings');put(city,0xd8,1); // non-study player excluded
  const batch=rpc.drain();assert.equal(batch.records.length,4);
  assert.deepEqual(JSON.parse(JSON.stringify(batch.records.slice(1).map(r=>[r.passesPlotFund,r.passesCombinedFunds]))),
    [[true,true],[false,true],[true,false]]);
  const saved=batch.records[1];assert.equal(saved.treasuryQ8,130560);
  assert.equal(saved.accountedQ8,128000);assert.equal(saved.unaccountedQ8,2560);
  assert.deepEqual(JSON.parse(JSON.stringify(saved.savingsQ8)),[19200,8000,6400,12000]);
  assert.equal(saved.lineage.known,false); // no fabricated attribution
  // Existing selection midpoint observes all district types. Read only its
  // chosen cached column after validating CE's matrix/row alias schema.
  const build=0xd0000,rows=0xe0000,matrix=0xf0000,reservation=0x100000,row=rows+0x78;
  put(build,0x90,city);put(build,0x4c8,rows);put(build,0x4d8,2);
  put(build,0x518,matrix);put(build,0x520,80);put(build,0x528,80);
  put(rows,8,30);put(rows,12,5);put(row,8,31);put(row,12,5);
  put(row,0x20,matrix+160);put(row,0x48,reservation);put(reservation,0,77);
  put(row,0x51,0);put(row,0x55,1);put(row,0x57,0);put(row,0x5a,1);
  put(row,0x70,1);put(row,0x74,524295);put(matrix,180,91234);
  put(frame,0x40,31);put(frame,0x44,5);
  fire('selection',{rdi:p(build),rbp:p(frame),rax:p(5)});
  const chosen=rpc.drain().records[0];assert.equal(chosen.kind,'district-selection');
  assert.equal(chosen.turn,203);assert.equal(chosen.district,5);assert.equal(chosen.totalQ8,91234);
  assert.equal(chosen.reservation,77);assert.equal(chosen.completedDistrictFlag,false);
  assert.equal(chosen.existingFootprint,null);assert.equal(chosen.scoreStatus,'read');
  assert.equal(mem.get(matrix+180),91234); // observation left the bid untouched
  put(row,0x20,matrix);fire('selection',{rdi:p(build),rbp:p(frame),rax:p(5)});
  const missing=rpc.drain().records[0];assert.equal(missing.kind,'district-selection');
  assert.equal(missing.totalQ8,null);assert.equal(missing.scoreStatus,'row_matrix_alias_differs');
  cfg.districts=null;fire('selection',{rdi:p(build),rbp:p(frame),rax:p(5)});
  assert.equal(rpc.drain().records[0].scoreStatus,'district_count_unconfigured');cfg.districts=40;
  if(capturePlacement){
    const queue=0x110000,definition=0x120000,hook=hooks.get(points.preCreateDistrict);
    put(queue,0x1e8,city);put(city,0x1948,build);put(definition,0x14,5);put(row,0x20,matrix+160);
    const call={context:{rcx:p(queue),rdx:p(definition),r8:p(xy)}};
    hook.onEnter.call(call);put(matrix,180,999);hook.onLeave.call(call,p(1));
    const placed=rpc.drain().records;assert.equal(placed.length,2);
    assert.equal(placed[0].kind,'district-placement-enter');assert.equal(placed[0].totalQ8,91234);
    assert.equal(placed[1].totalQ8,91234);assert.equal(placed[1].returnedSuccess,true);
    assert.equal(placed[1].exactPlacementEntry,true);assert.equal(placed[1].recomputed,false);
    assert.equal(mem.get(matrix+180),999); // after-entry state was not overwritten
    hook.onEnter.call(call);hook.onLeave.call(call,p(0));
    assert.equal(rpc.drain().records[1].returnedSuccess,false);
    put(city,0xd8,6);hook.onEnter.call(call);hook.onLeave.call(call,p(1));put(city,0xd8,1);
    assert.equal(rpc.drain().records.length,0);
  }
  const ownership=hooks.get(points.setOwner),plotData=0xc0000;
  // Do not install any readable owner byte on the wrapper. Its +1c is NOT the
  // resolved plot-data owner; an accidental read must fault this fixture.
  put(plotData,0x28,(5<<16)|31);
  const ownershipCall={context:{rcx:p(plotData),rdx:p(1),r8:p(524295)}};
  ownership.onEnter.call(ownershipCall);ownership.onLeave.call(ownershipCall);
  const ownerRow=rpc.drain().records[0];assert.equal(ownerRow.requestedPlayer,1);
  assert.equal(ownerRow.requestedCity,524295);assert.equal(ownerRow.plot,5*74+31);
  assert.equal(ownerRow.ownerStatus,'not_measured_wrapper_has_no_qualified_owner_field');
  for(const field of ['ownerBefore','ownerAfter','ownerMatchesRequest'])assert.equal(field in ownerRow,false);
  const command={rdi:p(city),rbp:p(frame),r15:p(treasury),rbx:p(-25600),rcx:p(treasury),rdx:p(delta)};
  fire('xp1Debit',command);const waiting=rpc.freeze();assert.equal(waiting.frozen,false);assert.equal(waiting.active,1);
  put(treasury,0xa8,104960);fire('xp1DebitReturn',command);
  const frozen=rpc.freeze();assert.equal(frozen.frozen,true);assert.equal(frozen.active,0);
  const payment=rpc.drain().records[1];assert.equal(payment.kind,'purchase-debit-return');
  assert.equal(payment.measuredDeltaQ8,-25600);assert.equal(payment.deltaMatched,true);
  assert.equal(payment.lineage.known,false);assert.equal(frozen.faults.length,0);
  assert.equal(hooks.size,capturePlacement?20:19); // freeze never detaches from a live instruction path
  return {hooks:hooks.size,debits:frozen.totals.commandDebits};
}
fixture(true);fixture(false,true);const report=fixture();report.placementHooks=fixture(false,false,true).hooks;console.log(JSON.stringify(report));
"""


if __name__=='__main__':
    unittest.main()
