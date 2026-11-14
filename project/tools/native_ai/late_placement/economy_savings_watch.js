'use strict';
// DIAGNOSTIC ONLY. Native Economic facts -> host journal -> offline CSC target
// joins. Nothing here bids, buys, resolves handles by calling the engine, changes
// arguments/registers/returns or writes target data. Frida's instruction hooks
// remain installed until controller-owned process exit. All RVAs/layouts below
// are for XP2 SHA092abfbb, text matched to reference SHA324c51e9. Evidence:
// AI-N109/114/116/117/119/129 and plot_purchase_observer.js. They are not a CE API.
const ECONOMY_SHA='092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f';
const ECONOMY_POINTS={activate:0x457120,routine:0x458530,cityQuote:0x459169,
  savings:0x45918f,requestBuilt:0x4591f3,commandChecked:0x45921f,commandReturned:0x459241,
  baseQuote:0x681346,baseDebit:0x681379,baseDebitReturn:0x68137e,baseAnnexReturn:0x6813a2,
  xp1Quote:0x71c63e,xp1Debit:0x71c671,xp1DebitReturn:0x71c676,xp1AnnexReturn:0x71c69a,
  treeInstalled:0x3e10fd,selection:0x3e0f3c,purchaseInitialized:0x55dc9f,setOwner:0x616a0};
const ECONOMY_GUARDS={receiverSave:0x459095,receiverFrame:0x4590a5};
// Named byte offsets. Economic arrays contain four signed-Q8 Gold values; 256
// equals one Gold, not a district utility point. Counts/weights are integers.
const E={player:0x98,accounted:0x120,totalWeight:0x1c8,weights:0x1e0,
  weightCount:0x1f0,savings:0x250};
const L={playerId:0xd8,treasury:0x780,gold:0xa8,cityId:0xa8,cityOwner:0xd8,
  cityBuild:0x1948,buildCity:0x90,cachedXY:0x238,playerCities:0x6d0,
  citiesHead:0xd0,nodeCity:0,nodeNext:0x10,treeParent:0x120,treeControl:0x1b0,
  treeId:0x1c8,contractId:0x110,contractControl:0x128,contractPlayer:0x140,
  contractTarget:0x178,plotCoordinates:0x28,gameSlot:0xb8aa68,gameTurn:0xc0};
// Same SHA's CE target_identity.h / AIDistrictScores.cpp::read_matrix schema.
// These are cached total district utilities, signed Q8 UTILITY, not Gold. The
// installed DB catalogue supplies the column count; do not infer it from a
// possibly stale/partial matrix or assume a vanilla district enumeration.
const M={rows:0x4c8,rowCount:0x4d8,data:0x518,capacity:0x520,length:0x528,
  rowSize:0x78,x:8,y:12,rowScores:0x20,reservation:0x48,completedDistrict:0x51,
  eligible:0x55,frontier:0x57,owned:0x5a,rowOwner:0x70,rowCity:0x74};
let mod,cfg,installed=false,enabled=false,closing=false,frozen=false,stopReason=null;
let sequence=0,active=0,interval=null;
const records=[],faults=[],hooks=[],debits=new Map(),commands=new Map();
const contracts=new Map(),trees=new Map(),selections=new Map();
const totals={records:0,targetedSavings:0,commandDebits:0,unknownLineage:0,
  expiredBindings:0,accountSnapshots:0};
function fail(e){enabled=false;stopReason=stopReason||'observation_fault';if(faults.length<16)faults.push(String(e));}
function emit(kind,row){
  if(records.length>=cfg.maxRecords)throw Error('Economic journal capacity; drain more frequently');
  records.push({sequence:++sequence,kind,...row});totals.records++;
}
function s32(p,o=0){return p.add(o).readS32();}
function address(p,o=0){return p.add(o).readPointer();}
function turn(){return s32(address(mod.base,L.gameSlot),L.gameTurn);}
function inWindow(t){return enabled&&t>=cfg.start&&t<=cfg.through&&
  interval&&t>=interval.after&&t<=interval.through;}
function who(city){return {player:s32(city,L.cityOwner),city:s32(city,L.cityId),cityPointer:city.toString()};}
function originalAI(player){return cfg.players.includes(player);}
function xy(x,y){if(!Number.isInteger(x)||!Number.isInteger(y)||x<0||x>=cfg.width||y<0||y>=cfg.height)
  throw Error('Economic coordinates outside configured map');return {x,y,plot:y*cfg.width+x};}
function requestXY(p){return xy(s32(p),s32(p,4));}
function common(context,reg){const city=context[reg],identity=who(city);
  if(!originalAI(identity.player))return null;
  const t=turn();if(!inWindow(t))return null;
  return {turn:t,...identity,...requestXY(context.r12)};}
function accounts(economic){
  const player=address(economic,E.player),id=s32(player,L.playerId);
  if(!originalAI(id))return null;
  if(s32(economic,E.weightCount)!==4)throw Error('Economic weights vector count differs');
  const funds=address(economic,E.savings),weights=address(economic,E.weights);
  const savingsQ8=[0,4,8,12].map(o=>s32(funds,o));
  const savingWeights=[0,4,8,12].map(o=>s32(weights,o));
  const totalWeight=s32(economic,E.totalWeight);
  if(savingWeights.some(v=>v<0)||totalWeight<=0||savingWeights.reduce((a,b)=>a+b,0)!==totalWeight)
    throw Error('Economic weights do not reconcile');
  const treasuryQ8=s32(address(player,L.treasury),L.gold),accountedQ8=s32(economic,E.accounted);
  return {player:id,economicPointer:economic.toString(),treasuryQ8,accountedQ8,
    unaccountedQ8:treasuryQ8-accountedQ8,savingsQ8,savingWeights,totalWeight};
}
function readableSpan(p,bytes){
  if(p.isNull()||!Number.isSafeInteger(bytes)||bytes<=0)return false;
  const span=Process.findRangeByAddress(p);
  return !!span&&span.protection.includes('r')&&p.compare(span.base)>=0&&
    p.add(bytes).compare(span.base.add(span.size))<=0;
}
function selectedValue(build,selection){
  const missing=reason=>({totalQ8:null,reservation:null,existingFootprint:null,scoreStatus:reason});
  if(cfg.districts==null)return missing('district_count_unconfigured');
  try{
    if(selection.district>=cfg.districts)return missing('selected_district_outside_catalogue');
    if(!readableSpan(build,M.length+4))return missing('city_build_unreadable');
    const identity=who(address(build,L.buildCity));
    if(identity.player!==selection.player||identity.city!==selection.city)return missing('city_identity_changed');
    const count=build.add(M.rowCount).readU32(),length=build.add(M.length).readU32(),capacity=build.add(M.capacity).readU32();
    if(count<2||count>37||length!==count*cfg.districts||capacity<length||capacity>37*4096)
      return missing('matrix_bounds_differ');
    const rows=address(build,M.rows),matrix=address(build,M.data);
    if(!readableSpan(rows,count*M.rowSize)||!readableSpan(matrix,length*4))return missing('matrix_span_unreadable');
    let matched=null;
    for(let i=0;i<count;i++){
      const row=rows.add(i*M.rowSize);
      if(s32(row,M.x)!==selection.x||s32(row,M.y)!==selection.y)continue;
      if(matched)return missing('duplicate_selected_coordinates');
      const expected=matrix.add(i*cfg.districts*4);
      if(!address(row,M.rowScores).equals(expected))return missing('row_matrix_alias_differs');
      const reservationPointer=address(row,M.reservation);
      const reservationReadable=readableSpan(reservationPointer,4);
      // +51 means completed/unpillaged only. It cannot establish that a row is
      // empty: foundations and pillaged districts also clear it. CE resolves
      // those via DistrictAt, a native call deliberately forbidden here.
      matched={totalQ8:s32(expected,selection.district*4),
        reservation:reservationReadable?s32(reservationPointer):null,
        reservationStatus:reservationReadable?'read':'unreadable',existingFootprint:null,
        existingFootprintStatus:'not_queried_native_call_required',
        completedDistrictFlag:row.add(M.completedDistrict).readU8()!==0,
        row:i,rowOwner:row.add(M.rowOwner).readS16(),rowCity:s32(row,M.rowCity),
        eligible:row.add(M.eligible).readU8()!==0,owned:row.add(M.owned).readU8()!==0,
        frontier:row.add(M.frontier).readU8()!==0,scoreStatus:'read',scoreUnits:'Q8_utility'};
    }
    return matched||missing('selected_row_absent');
  }catch(e){return {...missing('matrix_read_failed'),scoreError:String(e)};}
}
function ancestry(tree){const path=[],seen=new Set();
  while(!tree.isNull()){
    const key=tree.toString();if(seen.has(key)||path.length>=32)throw Error('Purchase ancestry bound/cycle');
    seen.add(key);path.push(tree);const parent=address(tree,L.treeParent);
    if(parent.isNull())return {path,root:tree};tree=parent;
  }throw Error('Missing purchase tree root');
}
function trim(map,t){
  // Bounded identity caches are not native plans. Journal rows remain durable.
  // Requests older than 32 turns become unknown rather than joining stale or
  // reused native pointers. No synthetic relationship is invented on reload.
  for(const[k,v]of map)if(t-v.turn>32){map.delete(k);totals.expiredBindings++;}
  if(map.size>=4096)throw Error('Economic lineage cache bound');
}
function binding(target,t){const b=contracts.get(target.toString());if(!b)return {known:false};
  const p=ptr(b.contractPointer);
  if(t-b.turn>32||s32(p,L.contractId)!==b.contractId||s32(p,L.contractControl)!==b.ownerControl||
     s32(p,L.contractPlayer)!==b.player||s32(p,L.contractTarget)!==b.x||s32(p,L.contractTarget+4)!==b.y){
    contracts.delete(target.toString());return {known:false};
  }
  return {known:true,...b};
}
function midpoint(name,callback){hooks.push(Interceptor.attach(mod.base.add(ECONOMY_POINTS[name]),function(){
  if(!enabled&&!debits.size&&!commands.size)return;
  try{callback(this.context,this.threadId);}catch(e){fail(e);}
}));}
function paired(name,enter,leave){hooks.push(Interceptor.attach(mod.base.add(ECONOMY_POINTS[name]),{
  onEnter(args){this.observed=null;if(!enabled)return;
    try{this.observed=enter(this.context,args,this.threadId,this.returnAddress);
      if(this.observed){if(active>=64)throw Error('Economic paired callback bound');active++;}}
    catch(e){this.observed=null;fail(e);}},
  onLeave(){const f=this.observed;if(!f)return;
    try{leave(f);}catch(e){fail(e);}finally{active--;}}
}));}
function snapshot(){return {installed,hooks:hooks.length,frozen,active:active+debits.size+commands.size,
  stopReason,faults:[...faults],totals:{...totals},buffered:records.length};}
function install(){
  // Windows x64 entry ABI: RCX=Economic*. Capture enclosing activation and the
  // routine purchaser separately. Differences across activate include allocation
  // AND spending; never label them a pure allocation or a per-site savings plan.
  for(const name of ['activate','routine'])paired(name,(c,args)=>{
    const economic=args[0],a=accounts(economic);if(!a)return null;
    const t=turn();if(!inWindow(t))return null;
    const result={turn:t,...a};totals.accountSnapshots++;
    if(name==='routine'){
      const player=address(economic,E.player),manager=address(player,L.playerCities);
      let node=address(manager,L.citiesHead);const seen=new Set(),candidates=[];
      while(!node.isNull()){
        const key=node.toString();if(seen.has(key)||seen.size>=256)throw Error('Economic city list bound/cycle');
        seen.add(key);const city=address(node,L.nodeCity),identity=who(city);
        if(identity.player!==a.player)throw Error('Economic city owner differs');
        const build=address(city,L.cityBuild),x=s32(build,L.cachedXY),y=s32(build,L.cachedXY+4);
        // Invalid sentinel means no cached routine candidate, not malformed XY.
        candidates.push({...identity,cached:x<0||y<0?null:xy(x,y)});
        node=address(node,L.nodeNext);
      }result.candidates=candidates;
    }
    emit(name+'-accounts-enter',result);return {economic,turn:t,player:a.player};
  },f=>{const a=accounts(f.economic);if(!a||a.player!==f.player)throw Error('Economic return identity differs');
    emit(name+'-accounts-leave',{turn:turn(),enteredTurn:f.turn,...a});});

  midpoint('cityQuote',(c)=>{const row=common(c,'rbp');if(row)emit('targeted-city-quote',{...row,gold:c.rax.toInt32()});});
  midpoint('savings',c=>{const row=common(c,'r14');if(!row)return;
    // TryPurchasePlot entry saves RCX at entryRSP+8. Seven pushes and 0x80 frame
    // move that word to currentRSP+c0. Saved slush/plot pointers are +d8/+d0.
    const economic=address(c.rsp,0xc0),funds=address(economic,E.savings);
    if(!funds.equals(address(c.rsp,0xd8))||!funds.add(8).equals(address(c.rsp,0xd0)))
      throw Error('Saved Economic/fund identity differs');
    const a=accounts(economic);if(!a||a.player!==row.player)throw Error('Economic/player differs');
    const gold=c.r15.toInt32(),factorQ8=c.rdi.toInt32(),plotQ8=a.savingsQ8[2],slushQ8=a.savingsQ8[0];
    if(gold<=0||gold>0x7fffff||factorQ8<0||factorQ8>256||
      plotQ8+slushQ8>0x7fffffff||plotQ8+slushQ8< -0x80000000)throw Error('Savings arithmetic range differs');
    const lineage=binding(c.r12,row.turn);if(!lineage.known)totals.unknownLineage++;
    totals.targetedSavings++;
    // Reconstructed predicates, not proof the subsequent branches ran. Gold
    // quote is whole Gold; funds/threshold are Q8. Bank alone is insufficient.
    emit('targeted-savings',{...row,...a,gold,factorQ8,plotQ8,slushQ8,minimumPlotFundQ8:gold*factorQ8,
      passesPlotFund:plotQ8>=gold*factorQ8,passesCombinedFunds:gold<=Math.floor((plotQ8+slushQ8)/256),lineage});
  });
  for(const name of ['requestBuilt','commandChecked','commandReturned'])midpoint(name,(c,thread)=>{
    const row=common(c,'r14');
    if(name==='commandReturned'){
      // Consume a previously observed admitted command even while freezing.
      const prior=commands.get(thread);if(prior){commands.delete(thread);
        emit('targeted-command-returned',{...prior,returnedTurn:turn()});}return;
    }
    if(!row)return;const accepted=(c.rax.toInt32()&255)!==0;
    emit(name==='requestBuilt'?'targeted-request-built':'targeted-command-checked',
      {...row,accepted,lineage:binding(c.r12,row.turn)});
    if(name==='commandChecked'&&accepted){if(commands.has(thread)||commands.size>=32)throw Error('Command pairing bound');
      commands.set(thread,{...row,lineage:binding(c.r12,row.turn)});}
  });
  // Both handlers are necessary in expansion games (AI-N117). Each payment's
  // CALL/return has identical thread+RSP; read actual Treasury before/after,
  // never count a requested delta or manager admission alone as money spent.
  for(const h of [{name:'base',x:0x67,y:0x6b,treasury:'r14',delta:'rsi'},
    {name:'xp1',x:0x38,y:0x3c,treasury:'r15',delta:'rbx'}]){
    const location=c=>{const identity=who(c.rdi);if(!originalAI(identity.player))return null;
      return {turn:turn(),...identity,...xy(s32(c.rbp,h.x),s32(c.rbp,h.y)),handler:h.name};};
    midpoint(h.name+'Quote',c=>{const row=location(c);if(row&&inWindow(row.turn))emit('purchase-quote',{...row,gold:c.rax.toInt32()});});
    midpoint(h.name+'Debit',(c,thread)=>{const row=location(c);if(!row||!inWindow(row.turn))return;
      const key=thread+':'+c.rsp,treasury=c.rcx;
      if(debits.has(key)||debits.size>=32||!treasury.equals(c[h.treasury]))throw Error('Payment receiver/pair bound');
      const prior=commands.get(thread);
      const f={...row,thread,key,treasury:treasury.toString(),deltaQ8:s32(c.rdx),treasuryBeforeQ8:s32(treasury,L.gold),
        lineage:prior&&prior.turn===row.turn&&prior.city===row.city&&prior.plot===row.plot?prior.lineage:{known:false}};
      debits.set(key,f);emit('purchase-debit-call',f);
    });
    midpoint(h.name+'DebitReturn',(c,thread)=>{const key=thread+':'+c.rsp,f=debits.get(key);if(!f)return;
      const row=location(c);if(!row||row.handler!==f.handler||row.cityPointer!==f.cityPointer||row.plot!==f.plot||
        !c[h.treasury].equals(ptr(f.treasury))||c[h.delta].toInt32()!==f.deltaQ8)throw Error('Unmatched purchase debit');
      const after=s32(ptr(f.treasury),L.gold);debits.delete(key);totals.commandDebits++;
      emit('purchase-debit-return',{...f,treasuryAfterQ8:after,measuredDeltaQ8:after-f.treasuryBeforeQ8,
        deltaMatched:after-f.treasuryBeforeQ8===f.deltaQ8});
    });
    midpoint(h.name+'AnnexReturn',c=>{const row=location(c);if(row&&inWindow(row.turn))
      emit('purchase-annex-return',row);});
  }
  // Fresh district selection -> installed tree -> purchase contract. Never
  // reinterpret an arbitrary XY pointer by subtracting a guessed object offset.
  // Control IDs are not city IDs. Only observed matching ancestry proves origin.
  midpoint('selection',(c,thread)=>{const city=address(c.rdi,L.buildCity),identity=who(city),t=turn();
    if(!originalAI(identity.player)||!inWindow(t))return;
    const x=s32(c.rbp,0x40),y=s32(c.rbp,0x44),district=c.rax.toInt32();
    if(district<0){selections.delete(thread);return;}
    if(selections.size>=32&&!selections.has(thread))throw Error('Selection thread bound');
    const selection={turn:t,...identity,...xy(x,y),district,build:c.rdi.toString(),frame:c.rbp.toString()};
    // Immediately after GetBestDistrict returns, before its result is consumed
    // by the preparation tree. This is an observed native choice, NOT proof a
    // request was accepted or a foundation appeared. It covers all selected
    // district types in scoped AI cities, including unmodified vanilla columns.
    // Missing optional cache evidence must not erase the exact choice receipt.
    emit('district-selection',{...selection,...selectedValue(c.rdi,selection)});
    selections.set(thread,selection);
  });
  midpoint('treeInstalled',(c,thread)=>{const city=address(c.rdi,L.buildCity),identity=who(city),t=turn();
    if(!originalAI(identity.player)||!inWindow(t))return;
    const chain=ancestry(c.rbx),rootTreeId=s32(chain.root,L.treeId);
    if(rootTreeId!==c.rsi.toInt32())throw Error('Installed root identity differs');
    const pending=selections.get(thread);selections.delete(thread);trim(trees,t);
    const selection=pending&&pending.turn===t&&pending.build===c.rdi.toString()&&pending.frame===c.rbp.toString()?pending:null;
    const row={turn:t,...identity,treePointer:c.rbx.toString(),rootPointer:chain.root.toString(),rootTreeId,
      ownerControl:s32(chain.root,L.treeControl),selection};trees.set(c.rbx.toString(),row);
    emit('district-purchase-tree',row);
  });
  midpoint('purchaseInitialized',c=>{const player=s32(c.rbp,L.playerId),t=turn();if(!originalAI(player)||!inWindow(t))return;
    const p=c.r15,chain=ancestry(c.rsi),ownerControl=s32(p,L.contractControl),rootTreeId=s32(chain.root,L.treeId);
    if(s32(p,L.contractPlayer)!==player||ownerControl!==s32(chain.root,L.treeControl))throw Error('Contract/root player differs');
    trim(trees,t);trim(contracts,t);
    const origins=chain.path.map(tree=>trees.get(tree.toString())).filter(v=>v&&v.player===player&&
      v.rootPointer===chain.root.toString()&&v.rootTreeId===rootTreeId&&v.ownerControl===ownerControl);
    const cities=[...new Set(origins.map(v=>v.city))];
    const row={turn:t,player,...requestXY(p.add(L.contractTarget)),contractPointer:p.toString(),
      contractId:s32(p,L.contractId),ownerControl,rootTreeId,originCity:cities.length===1?cities[0]:null,
      selection:origins.length&&cities.length===1?origins[0].selection:null};
    contracts.set(p.add(L.contractTarget).toString(),row);emit('purchase-contract-created',row);
  });
  // SetOwner is a compact ownership pathway, not a universal proof of payment.
  // Filter its requested player before any pointer reads; no stackwalk/plot scan.
  // AI-N129 correction: receiver is a plot WRAPPER. Owner +1c belongs to the
  // resolved data behind virtual slots+30/+38, not this receiver. Full bodies
  // of SetOwner616a0 and PurchasePlotContract Update3fa260 match reference and
  // current binaries, but that does not make offsets portable between objects.
  // Do not call a native getter or guess another offset here. Requested owner/
  // city and qualified wrapper coordinates are the only facts collected.
  // Actual ownership comes from strictly later Lua snapshots; SetOwner also
  // handles culture growth, so a return alone never proves payment or ownership.
  paired('setOwner',c=>{const player=c.rdx.toInt32();if(!originalAI(player))return null;
    const t=turn();if(!inWindow(t))return null;const packed=s32(c.rcx,L.plotCoordinates);
    return {turn:t,...xy((packed<<16)>>16,packed>>16),requestedPlayer:player,requestedCity:c.r8.toInt32(),
      plotPointer:c.rcx.toString(),ownerStatus:'not_measured_wrapper_has_no_qualified_owner_field'};
  },f=>emit('plot-set-owner-return',f));
}
rpc.exports={
  init(spec,config){
    if(installed||hooks.length)throw Error('Economic observer already initialized');
    if(Process.platform!=='windows'||Process.arch!=='x64'||Process.pointerSize!==8||
      spec.sha256!==ECONOMY_SHA||spec.name!=='GameCore_XP2_FinalRelease.dll'||config.maxRecords!==20000||
      !Number.isInteger(config.start)||!Number.isInteger(config.through)||config.start<0||
      config.through<=config.start||config.through-config.start>300||
      !Array.isArray(config.players)||!config.players.length||new Set(config.players).size!==config.players.length||
      config.players.some(p=>!Number.isInteger(p)||p<1||p>5)||
      config.districts!=null&&(!Number.isInteger(config.districts)||config.districts<1||config.districts>4096)||
      !Number.isInteger(config.width)||!Number.isInteger(config.height)||config.width<1||config.width>256||
      config.height<1||config.height>256)throw Error('Unqualified Economic scope');
    mod=Process.getModuleByName(spec.name);cfg=config;
    if(mod.path.replace(/\\/g,'/').toLowerCase()!==spec.path.replace(/\\/g,'/').toLowerCase()||mod.size!==spec.imageSize)
      throw Error('Different loaded Economic module');
    const pe=mod.base.add(0x3c).readU32();
    if(mod.base.add(pe+8).readU32()!==spec.timestamp)throw Error('Different loaded PE timestamp');
    // Host checks the whole file. Validate every midpoint/entry in memory BEFORE
    // installing any hook: a CE detour or another observer must not be ignored.
    for(const[name,rva]of Object.entries({...ECONOMY_POINTS,...ECONOMY_GUARDS})){
      const p=spec.points[name];if(!p||p.rva!==rva||!/^[0-9a-f]{64}$/.test(p.prefix))throw Error('Wrong entry '+name);
      const bytes=new Uint8Array(mod.base.add(rva).readByteArray(32));
      const actual=Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');
      if(actual!==p.prefix)throw Error('Loaded entry differs '+name);
    }
    interval={after:cfg.start,through:cfg.start};install();installed=true;Interceptor.flush();return snapshot();
  },
  start(){if(!installed||closing||stopReason)throw Error('Economic observer unready');enabled=true;return snapshot();},
  window(after,through){if(closing||!Number.isInteger(after)||!Number.isInteger(through)||after<cfg.start||
    through<after||through>cfg.through)throw Error('Invalid Economic window');interval={after,through};return snapshot();},
  drain(){const result={...snapshot(),records:records.splice(0)};return result;},
  freeze(){enabled=false;closing=true;frozen=active===0&&debits.size===0&&commands.size===0;return snapshot();}
};
