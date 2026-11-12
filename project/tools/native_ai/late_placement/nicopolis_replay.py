"""Replay source-identified plot-purchase cases through the shared controller.

This diagnostic observes the ordinary district selector, purchase attempts
and plot state. Integrated treatment stages main CSC AI plus its UI quote
bridge. Its matched ablation suppresses only positive frontier offers. The
historical Nicopolis frontier mode injects one early deduction into its old
carrier; it is not shipped policy. All fixtures share exclusive ownership,
bounded native receipt streams and verified restoration.

The explicit Szeged buyer prototype changes only the staged copy's quote
screen and, in restrict mode, the known contract's competing native buyer.
It is not a shipping setting or general CE API.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sys
import traceback
import time
from types import SimpleNamespace

from ce_bakers_fresh import package_identity
from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from driver import (
    HERE, STUDY, HOTFIX_SHA, XP2_IMAGE_SIZE, HeldProcess, NativeSession, configure,
    flags, launch, load, make_probe_controller, manifest, native_inventory, parse, read,
    restore_preferences, sha, write_json, lua,
)
from nuremberg_purchase_policy import source_checkpoint as nuremberg_checkpoint, owned_checkpoint
from supplier_purchase_policy import PREPARE as PREPARE_SUPPLIER, INSPECT as INSPECT_SUPPLIER, without_supplier_bid
from full_game_controller.checkpoint import save_inactive_boundary

CE_SHA = 'f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07'
SAVE_SHA = 'e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a'
PACKAGES = ('CSC Bakers Development CE', 'CSC Bakers Development Mod')
SCANNER = Path('Lua_UI/AI/CSC_AI_AdjacencyScan.lua')
QUOTE_BRIDGE = Path('Lua_UI/Adjacencies/CSC_AdjacencyUI.lua')
LOGS = ('Lua.log', 'AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv')

# Explicit, source-identified fixtures share lifecycle and instrumentation.
# The Szeged case is a viable +3 later-stage customer prospect, not a +4 or
# Stage 2 Harbor claim. Its source bank/quotes must qualify again before play.
CASES = {
    'nicopolis': dict(sha256=SAVE_SHA, player=1, city=524295, name='LOC_CITY_NAME_NICOPOLIS',
        profile='BAKERS', district=36, plots=[398,472,401], purchasePlots=[398,401]),
    'szeged': dict(sha256='c50976621de17e38f998fad916b22a1bd219f4cdc9af508d90b8846d011fbf91',
        player=2,city=589829,name='LOC_CITY_NAME_SZEGED',profile='TAILORS',district=37,
        plots=[1365],purchasePlots=[1365]),
    # Common diagnostic release, not a bought tile. The separate source ledger
    # and inactive202 save must qualify again before observing native payment.
    'nuremberg':dict(sha256='d579ecc2c54909f1b21aaa96caad237daeb9fc0f67cd78c8602191c70c2a9026',
        player=3,city=458758,name='LOC_CITY_NAME_NUREMBERG',profile='BAKERS',district=36,
        turn=202,archive='source.Civ6Save',plots=[788,861,713],purchasePlots=[788]),
}
CASES['nuremberg-reload']=dict(CASES['nuremberg'],turn=205,archive='endpoint.Civ6Save',
    metadata='endpoint-checkpoint.json',sha256='6977d48d856ea1f08f8f1876371898495a3e182d9b8d7cffbee0de09fdab1a03')
CASES['nuremberg-supplier-prepare']=dict(CASES['nuremberg'],turn=216,
    metadata='endpoint-checkpoint.json',archive='endpoint.Civ6Save',purchasePlots=[861],
    sha256='22998f016e31272f53e1d1f4a1446b954c0aa9688c5072a74d9694f181b80fc8')
CASES['nuremberg-supplier']=dict(CASES['nuremberg-supplier-prepare'],
    sha256='9eff6d6c10e7c95af1f5ac37ee64c364f3174e4beefd1116c33769a905ff1d49')
CASES['nuremberg-supplier-follow']=dict(CASES['nuremberg-supplier'],turn=224,max_turn=230,
    sha256='858c4af2ebedc72ae2ecd0e81f3b438651f018354f795b550db2670e739d855b')

# This untuned save intentionally predates the policy's persisted seat metadata.
# A diagnostic may seed it from these acknowledged turn-1 records, never from
# current autoplay IsHuman. Pin the provenance as well as the existing save pin.
SZEGED_SEAT_PROVENANCE = {
    'source.json':'78ba15dbf5e3cd294f348fa4f8fcaa2452acc878cfeebc1ecfdfcd12202ba827',
    'protocol.json':'7580f6ef2b91df169194e06047317c42d52d03521483cfedd895c11d3c41da8e',
    'checkpoint.json':'b6ddc2beba796c37ed4d772b0302d2cf4e0a1f7910478b310ee1d21d14e7fde5',
    'commands/0011-fresh-start-identity.lua':'1e106ef8430e4f49e373015f3ab6fd90934a127bce70e5f78ab41779241cb1e7',
    'commands/0011-fresh-start-identity.txt':'0e82197375287974257aedab7082e023f7ca9073b13bf85edfb155f72c71b5ab',
}


def seed_source_seats(source, checkpoint, case):
    assert case==CASES['szeged'],'Seat migration is qualified only for the pinned untuned Fractal fixture'
    for name,digest in SZEGED_SEAT_PROVENANCE.items():
        assert sha(checkpoint/name)==digest,'Original-seat provenance differs: '+name
    original=load(checkpoint/'source.json')
    assert original['original_ai']==[1,2,3,4,5]
    assert load(checkpoint/'protocol.json')['untuned'] is True
    seats=[dict(player=r['player'],leader=r['leader'],human=0 if r['player'] in original['original_ai'] else 1)
        for r in original['starts']]
    assert [r['player'] for r in seats]==list(range(6))
    # Validate the WHOLE set before any property write. Preserve matching
    # existing values and abort on conflict. Identical bytes are staged in
    # both buyer arms; this is not a production late-save migration feature.
    prefix='''-- DIAGNOSTIC ONLY: seed missing original-seat metadata from pinned turn-1 provenance.
do
 local seats=__SEATS__
 assert(Game.GetCurrentGameTurn()==200,'Seat fixture turn changed')
 local missing={}
 for _,r in ipairs(seats) do
  local p=assert(Players[r.player]);local config=assert(PlayerConfigurations[r.player])
  assert(config:GetLeaderTypeName()==r.leader,'Seat fixture leader changed')
  assert(p:IsHuman()==(r.human==1),'Seat fixture current controller changed')
  local key='CSC_AI_OriginalHuman_'..r.player
  local previous=Game:GetProperty(key)
  assert(previous==nil or previous==r.human,'Conflicting original-seat metadata')
  print('CSC_DIAGNOSTIC_SOURCE_SEAT',r.player,tostring(previous),r.human)
  if previous==nil then missing[#missing+1]={key=key,value=r.human} end
 end
 for _,r in ipairs(missing)do Game:SetProperty(r.key,r.value)end
 print('CSC_DIAGNOSTIC_SOURCE_SEATS_SEEDED',#missing)
end
'''.replace('__SEATS__',lua(seats))
    return prefix.encode('utf-8')+source,dict(files=SZEGED_SEAT_PROVENANCE,seats=seats)

# The source property reads are diagnostic only. Unowned neighboring deposits
# are logged separately because ReadSuppliers intentionally counts owned supply.
WATCHER = """
local placement=assert(CSC_AI_QuarterPlacement)
local scope=__SCOPE__
local profile
for _,p in ipairs(placement.StageTwoProfiles())do if p.key==scope.profile then profile=p end end
assert(profile and profile.district.Index==scope.district)
local player=Players[scope.player]
function CSC_PURCHASE_Snapshot()
    local turn=Game.GetCurrentGameTurn()
    if turn<200 or turn>__ENDPOINT__ then return end
    for _,index in ipairs(scope.plots) do
        local plot=assert(Map.GetPlotByIndex(index))
        local buyer=Cities.GetPlotPurchaseCity(plot)
        local supply=placement.ReadSuppliers(player,plot,profile)
        print('CSC_PURCHASE_SNAPSHOT',turn,index,plot:GetOwner(),buyer and buyer:GetID() or -1,
            plot:GetDistrictType(),#supply.base,#supply.specialty,
            plot:CanHaveDistrict(profile.district.Index,scope.player,scope.city))
        for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
            local resource=GameInfo.Resources[neighbor:GetResourceType()]
            local revealed=PlayersVisibility[scope.player]:IsRevealed(neighbor:GetX(),neighbor:GetY())
            local visible=resource and revealed and CSC_Adjacency.ResourceVisible(scope.player,resource.Index)
            local district=GameInfo.Districts[neighbor:GetDistrictType()]
            print('CSC_PURCHASE_SITE_NEIGHBOR',turn,index,neighbor:GetIndex(),neighbor:GetOwner(),revealed,
                visible and resource.ResourceType or '-',neighbor:GetImprovementType(),
                district and district.DistrictType or '-',
                visible and CSC_Adjacency.HasTag(profile.base,resource.ResourceType) or false,
                visible and CSC_Adjacency.HasTag(profile.specialty,resource.ResourceType) or false,
                profile.customers[neighbor:GetDistrictType()]~=nil,
                district and CSC_Adjacency.HasTag('CLASS_CSC_'..profile.key..'_SALES',district.DistrictType) or false)
        end
    end
    local city=assert(CityManager.GetCity(scope.player,scope.city))
    print('CSC_PURCHASE_CITY',turn,city:GetName(),city:GetPopulation(),city:GetBuildQueue():CurrentlyBuilding())
    -- Physical completion is independent of the request's COMPLETED log.
    local districts=city:GetDistricts()
    for index=0,districts:GetNumDistricts()-1 do
        local district=districts:GetDistrictByIndex(index)
        if district and district:GetType()==scope.district then
            local plot=assert(Map.GetPlot(district:GetX(),district:GetY()))
            print('CSC_PURCHASE_DISTRICT_STATE',turn,scope.player,scope.city,plot:GetIndex(),
                district:GetType(),district:IsComplete(),district:IsPillaged())
        end
    end
    local candidate=Map.GetPlotByIndex(scope.purchasePlots[1])
    local candidateCity=Cities.GetPlotPurchaseCity(candidate)
    print('CSC_SUPPLIER_STATE',turn,candidate:GetIndex(),candidate:GetOwner(),candidateCity and candidateCity:GetID() or -1,
        candidate:GetResourceType(),candidate:GetImprovementType(),candidate:IsImprovementPillaged())
    for _,plot in ipairs(Map.GetAdjacentPlots(candidate:GetX(),candidate:GetY())) do
        local resource=GameInfo.Resources[plot:GetResourceType()]
        local revealed=PlayersVisibility[scope.player]:IsRevealed(plot:GetX(),plot:GetY())
        local visible=resource and revealed and CSC_Adjacency.ResourceVisible(scope.player,resource.Index)
        print('CSC_PURCHASE_NEIGHBOR',turn,plot:GetIndex(),plot:GetOwner(),revealed,
            visible and resource.ResourceType or '-',plot:GetDistrictType())
        if visible then
            print('CSC_PURCHASE_ADJACENT_RESOURCE',turn,plot:GetIndex(),plot:GetOwner(),
                resource.ResourceType,CSC_Adjacency.HasTag(profile.base,resource.ResourceType))
        end
    end
end
CSC_PURCHASE_Snapshot()
GameEvents.OnGameTurnStarted.Add(CSC_PURCHASE_Snapshot)
"""

FRONTIER_PROBE = b"""    -- Diagnostic fixture only. Plot 398 was admitted by the stock
    -- selector while unowned. Test one early entry without creating a
    -- purchase request or changing the native treasury/legality checks.
    if pid == 1 and district.Index == 36 then
        local site = Map.GetPlotByIndex(398)
        if site and site:GetOwner() == -1 and visibility:IsRevealed(site:GetX(), site:GetY())
            and #readSuppliers(player, site, profile).base == 0 then
            bids[#bids + 1] = {player=pid, city=524295, district=36, plot=398,
                delta=-noBasePenaltyQ8, weak=true}
        end
    end
"""


def entry_keys(profile):
    return {(row['id'], row['subscription'], row['file']) for row in profile['entries']}


def ablate_frontier_offer(source, case):
    # Counterfactual diagnostic only, applied to the staged copy. Preserve
    # all other players, owned offers and frontier deductions. This removes
    # the exact fixture pair from the new positive-candidate path; it does
    # not overwrite a native score or submit another action in its place.
    needle=b"and type(ui.GetPlotPurchaseQuote) == 'function' then"
    assert source.count(needle)==1
    # Nuremberg tests one footprint's acquisition guidance. Both supported
    # Quarters can promote that same land: leaving Tailors active would not
    # remove CSC's positive acquisition signal for the footprint. Other older
    # fixtures retain their declared individual district/site intervention.
    district_condition=('(district.Index == 36 or district.Index == 37)'
        if case==CASES['nuremberg'] else f"district.Index == {case['district']}")
    condition=(f"and type(ui.GetPlotPurchaseQuote) == 'function' and not "
        f"(pid == {case['player']} and city:GetID() == {case['city']} "
        f"and {district_condition} and index == {case['purchasePlots'][0]}) then")
    return source.replace(needle,condition.encode('ascii'))


def bypass_szeged_quote_screen(source, case):
    # Identical diagnostic bypass in observe/restrict arms. The production
    # UI file stays conservative. The shared controller holds the inactive
    # source until the prototype's scoped native instrumentation is armed.
    assert case==CASES['szeged']
    needle=b"    if not ok or type(value) ~= 'number' or value <= 0 then return nil; end"
    assert source.count(needle)==1
    newline=b'\r\n' if b'\r\n' in source else b'\n'
    addition=(b'    -- Diagnostic Szeged buyer prototype only; not shipping policy.'+newline
        +b'    if playerID == 2 and cityID == 589829 and plotIndex == 1365 then return value; end')
    return source.replace(needle,needle+newline+addition)


def qualify_integrated_policy(controller, out, case):
    # Loading the production files is not evidence that they publish anything.
    # In particular an untuned checkpoint has no original-seat properties;
    # the production safety gate deliberately refuses to infer them at turn200.
    # Capture every gate BEFORE asserting, without initializing the model or
    # changing identities. A failed qualification must stop before autoplay.
    code='local scope='+lua(case)+"""
local ui=ExposedMembers and ExposedMembers.CSC_Adjacency
local bridge=CSC_AI_DistrictBridge
print('CSC_POLICY_BRIDGE',bridge and bridge.Available() or false)
print('CSC_POLICY_SINGLE_PLAYER',ui and type(ui.IsSinglePlayer)=='function' and ui.IsSinglePlayer() or false)
print('CSC_POLICY_NATIVE',bridge and bridge.Status() or 'unavailable')
if bridge and type(CE_AIDistrictScoresReceipt)=='function' then
 local status=bridge.Status()
 local version=status and tonumber(status:match('"version":(%d+)'))
 if version then print('CSC_POLICY_TARGET_RECEIPT',
  CE_AIDistrictScoresReceipt(version,scope.player,scope.city,scope.district,scope.purchasePlots[1])) end
end
for _,p in ipairs(PlayerManager.GetAliveMajors()) do
 local original=Game:GetProperty('CSC_AI_OriginalHuman_'..p:GetID())
 print('CSC_POLICY_SEAT',p:GetID(),tostring(original),p:IsHuman())
end
local profile
for _,p in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do if p.key==scope.profile then profile=p end end
print('CSC_POLICY_BASE_TAG',profile and profile.base or 'missing',
 profile and CSC_Adjacency.Tags[profile.base]~=nil or false)
"""
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','qualify-integrated-policy')
    (out/'policy-qualification.txt').write_text(raw,encoding='utf-8')
    statuses=re.findall(r'CSC_POLICY_NATIVE\t(\{[^\r\n]+\})',raw)
    status=json.loads(statuses[0]) if len(statuses)==1 else None
    seats=[dict(player=int(pid),originalHuman=None if original=='nil' else int(original),human=human=='true')
        for pid,original,human in re.findall(r'CSC_POLICY_SEAT\t(\d+)\t(nil|0|1)\t(true|false)',raw)]
    target=next((seat for seat in seats if seat['player']==case['player']),None)
    verified=(bool(re.search(r'CSC_POLICY_BRIDGE\ttrue',raw))
        and bool(re.search(r'CSC_POLICY_SINGLE_PLAYER\ttrue',raw))
        and status is not None and status.get('ready')==1 and status.get('faults')==0
        and status.get('enabled')==1 and status.get('version',0)>0
        and target is not None and target['originalHuman']==0 and not target['human']
        and bool(re.search(r'CSC_POLICY_BASE_TAG\t[^\t\r\n]+\ttrue',raw)))
    receipts=re.findall(r'CSC_POLICY_TARGET_RECEIPT\t(\{[^\r\n]+\})',raw)
    target_receipt=json.loads(receipts[0]) if len(receipts)==1 else None
    write_json(out/'policy-qualification.json',dict(verified=verified,native=status,seats=seats,targetReceipt=target_receipt))
    assert verified,'Integrated policy is inactive or unqualified; inspect policy-qualification.json before autoplay'


def qualify_purchase(controller, out, case, allow_tied=False):
    # Fixture qualification only. Never expose this current-bank test as a
    # live policy gate: native Economic is allowed to retain a plan and save.
    # Quotes from every city identify ambiguity before autoplay. The live
    # attempt observer still records which buyer actually wins later.
    assert not allow_tied or case==CASES['szeged']
    code='local scope='+lua(case)+'\nlocal allowTied='+('true' if allow_tied else 'false')+"""
local player=assert(Players[scope.player])
local city=assert(CityManager.GetCity(scope.player,scope.city))
assert(not player:IsHuman() and city:GetName()==scope.name)
local target=scope.purchasePlots[1]
local plot=assert(Map.GetPlotByIndex(target))
assert(plot:GetOwner()==-1 and plot:GetDistrictType()==-1,'Fixture footprint already occupied')
local row=assert(GameInfo.Districts[scope.district])
local quote,buyer,count,proposerQuote
count=0
local quotes={}
for _,c in player:GetCities():Members()do
 local q=c:GetGold():GetPlotPurchaseCost(target)
 print('CSC_PURCHASE_CITY_QUOTE',c:GetID(),c:GetName(),target,tostring(q))
 count=count+1
 quotes[#quotes+1]={city=c:GetID(),quote=q}
 if c:GetID()==scope.city then proposerQuote=q end
 if q and q>0 and(not quote or q<quote)then quote,buyer=q,c:GetID()end
end
if allowTied then
 -- Deliberately ambiguous diagnostic pair, not ordinary purchase qualification.
 assert(proposerQuote and proposerQuote>0 and quote==proposerQuote,'Prototype proposer is not a cheapest buyer')
 local ties=0
 for _,r in ipairs(quotes)do if r.quote==proposerQuote then ties=ties+1 end end
 assert(ties>=2,'Expected prototype buyer ambiguity changed')
 quote=proposerQuote
else
 assert(quote and buyer==scope.city,'Fixture has no unambiguous proposing-city purchase quote')
 for _,r in ipairs(quotes)do
  assert(r.city==buyer or not r.quote or r.quote<=0 or r.quote>quote,'Fixture buyer quote tied')
 end
end
local bank=player:GetTreasury():GetGoldBalance()
assert(bank>=quote,'Fixture lacks actual Treasury for its source quote')
local queue=city:GetBuildQueue()
local function optional(object,method,...)
 if not object or type(object[method])~='function' then return 'unknown' end
 local ok,value=pcall(object[method],object,...)
 if ok and value~=nil then return value end
 return 'unknown'
end
print('CSC_PURCHASE_QUALIFIED',Game.GetCurrentGameTurn(),scope.player,scope.city,target,quote,bank,count,
 optional(queue,'CanProduce',row.Hash,false,true),
 optional(queue,'GetCurrentProductionTypeHash'),
 optional(city:GetDistricts(),'GetNumAllowedDistrictsRequiringPopulation'),
 optional(city:GetDistricts(),'GetNumZonedDistrictsRequiringPopulation'))
"""
    raw=controller.cmd(code,'PlotInfo','qualify-source-purchase')
    (out/'source-purchase-qualification.txt').write_text(raw,encoding='utf-8')
    matches=re.findall(r'CSC_PURCHASE_QUALIFIED\t'+str(case.get('turn',200))+r'\t(\d+)\t(\d+)\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)\t(\d+)',raw)
    assert len(matches)==1,'Missing purchase fixture qualification'
    pid,city,plot,quote,bank,count=matches[0]
    assert (int(pid),int(city),int(plot))==(case['player'],case['city'],case['purchasePlots'][0])
    assert float(bank)>=float(quote)>0
    assert len(re.findall(r'CSC_PURCHASE_CITY_QUOTE\t',raw))==int(count)
    write_json(out/'source-purchase-qualification.json',dict(verified=True,player=int(pid),city=int(city),
        plot=int(plot),quote=float(quote),treasuryGold=float(bank),cities_quoted=int(count),
        purpose='buyer-prototype' if allow_tied else 'unambiguous-purchase',ambiguousBuyer=allow_tied))


def run(args):
    case_name = getattr(args, 'case', 'nicopolis')
    case = dict(CASES[case_name])
    source_turn=case.get('turn',200)
    out = args.output.resolve()
    home, user_root = args.my_games.resolve(), args.user_root.resolve()
    reference = args.reference.resolve(strict=True)
    checkpoint = args.checkpoint.resolve(strict=True)
    assert not out.exists() and not native_inventory(), 'Fresh output and exclusive native session required'
    prepare_supplier=case_name=='nuremberg-supplier-prepare'
    supplier_case=case_name.startswith('nuremberg-supplier')
    assert (source_turn < args.through <= case.get('max_turn',224) or prepare_supplier and args.through==source_turn), 'This fixture uses a bounded continuation of its verified source'
    assert not prepare_supplier or args.mode=='integrated' and args.save_endpoint
    assert load(reference / 'complete.json')['verified']
    assert load(reference / 'session-closed.json')['verified']
    meta = load(checkpoint / case.get('metadata','checkpoint.json'))
    save = Path(meta['native_save']).resolve(strict=True)
    assert meta['verified'] and meta['turn'] == source_turn and meta['sha256'] == case['sha256']
    assert save.parent == (home / 'Saves/Single').resolve()
    assert sha(save) == sha(checkpoint / case.get('archive','endpoint.Civ6Save')) == case['sha256']
    source_policy=getattr(args,'source_policy_root',None) or args.policy_root
    if case_name=='nuremberg-supplier-follow':
        # Follow the paid, owned supplier while the already-assigned native
        # Builder travels. This is not a new common fixture or a new purchase.
        assert load(checkpoint/'complete.json')==dict(verified=True,turns_advanced=8)
        assert load(checkpoint/'session-closed.json')['verified']
        parent=load(checkpoint/'inputs.json')
        assert parent['case']==CASES['nuremberg-supplier'] and not parent['supplier_no_bid']
        trace=load(checkpoint/'purchase-trace.json');assert trace['fault']is None
        debits=[r for r in trace['records']if r['kind']=='debit-return'and r.get('plot')==861]
        assert len(debits)==1 and debits[0]['city']==458758 and debits[0]['deltaMatched'] and debits[0]['measuredDeltaQ8']==-45*256
        assert meta['save_complete_event'] and meta['native_phase_unchanged']
        assert all(meta[p]['turn']==224 and not meta[p]['active'] and meta[p]['local_player']==0 and meta[p]['player0_human']for p in ('before','after'))
        for relative in (SCANNER,Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'),QUOTE_BRIDGE,
                Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua'),Path('Lua_UI/AI/CSC_AI_DistrictBridge.lua')):
            assert sha(source_policy/relative)==parent['packages']['CSC Bakers Development Mod'][str(relative)]['sha256']
    elif case_name=='nuremberg-supplier':
        assert load(checkpoint/'prepared-source-audit.json')['verified']
        assert load(checkpoint/'session-closed.json')['verified']
        assert load(checkpoint/'supplier-preparation.json')['native_purchase'] is False
        assert meta['save_complete_event'] and meta['native_phase_unchanged']
        assert all(meta[p]['turn']==216 and not meta[p]['active'] and meta[p]['player0_human'] for p in ('before','after'))
    elif prepare_supplier:
        assert load(checkpoint/'complete.json')==dict(verified=True,turns_advanced=14)
        assert load(checkpoint/'session-closed.json')['verified']
        parent=load(checkpoint/'inputs.json')
        assert parent['mode']=='integrated' and not parent['repairOwnedPurchase']
        for relative in (SCANNER,Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'),QUOTE_BRIDGE,
                Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua'),Path('Lua_UI/AI/CSC_AI_DistrictBridge.lua')):
            assert sha(source_policy/relative)==parent['packages']['CSC Bakers Development Mod'][str(relative)]['sha256']
    elif case_name=='nuremberg':
        # Source provenance and treatment code are distinct. A new integrated
        # adapter intentionally changes main Lua; qualify the save against its
        # recorded historical main files, then pin the current staged treatment.
        source_policy=getattr(args,'source_policy_root',None) or args.policy_root
        qualified=nuremberg_checkpoint(checkpoint,home,SAVE_SHA,source_policy)
        assert qualified['sha256']==case['sha256']
        released=load(checkpoint/'release-preparation.json')
        assert released['verified'] and released['released_plot']==788 and released['native_purchase'] is False
    elif case_name=='nuremberg-reload':
        source_policy=args.source_policy_root
        assert owned_checkpoint(checkpoint,home,source_policy)['sha256']==case['sha256']
    packages = {reference / name: home / 'Mods' / name for name in PACKAGES}
    original_pins = {source: manifest(source) for source in packages}
    pins = {source: dict(value) for source, value in original_pins.items()}
    ce, csc = packages
    ce_id, _ = package_identity(ce)
    csc_id, _ = package_identity(csc)
    test_ids = {ce_id, csc_id}
    ce_relative = Path('Binaries/Win64') / DLL
    assert sha(ce / ce_relative) == CE_SHA
    ownership_dll=getattr(args,'ownership_ce_dll',None)
    ownership_bytes=ownership_dll.read_bytes() if ownership_dll else None
    effective_ce_sha=hashlib.sha256(ownership_bytes).hexdigest() if ownership_bytes else CE_SHA
    if ownership_bytes:
        assert effective_ce_sha==args.ownership_ce_sha,'Integrated CE build differs from the explicit qualified pin'
        pins[ce][str(ce_relative)]=dict(sha256=effective_ce_sha,size=len(ownership_bytes))
    binary = Path(load(reference / 'launch-bootstrap.json')['binary'])
    assert sha(binary) == HOTFIX_EXE_SHA
    recovery = args.recover_from.resolve(strict=True) if args.recover_from else None
    replacements = {}
    seat_provenance = None
    if case_name == 'nicopolis' and args.mode != 'original':
        original_run = args.original_run.resolve(strict=True)
        assert load(original_run / 'complete.json')['verified']
        trace = load(original_run / 'selector-trace.json')
        selected, = (row for row in trace['records'] if row['kind'] == 'selection' and row['turn'] == 203)
        assert selected['winner'] == dict(district=36, x=28, y=5, q8=396462)
        frontier, = (row for row in selected['sites'] if row['plot'] == 398)
        assert frontier['owned'] == 0 and frontier['frontier'] == 1 and frontier['reservation'] == -1
    if args.mode == 'frontier':
        assert case_name == 'nicopolis', 'One-tile historical probe belongs to Nicopolis only'
        before = (csc / SCANNER).read_bytes()
        newline = b'\r\n' if b'\r\n' in before else b'\n'
        needle = b'    return bids, counts' + newline + b'end'
        assert before.count(needle) == 1
        modified = before.replace(needle, FRONTIER_PROBE.replace(b'\n', newline) + needle)
        replacements[SCANNER] = modified
    elif args.mode == 'integrated':
        # Stage all four production AI modules and their UI quote bridge. Unrelated
        # worktree gameplay, art and content cannot enter this saved fixture.
        for relative in (SCANNER, Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'), QUOTE_BRIDGE,
                Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua'),Path('Lua_UI/AI/CSC_AI_DistrictBridge.lua')):
            replacements[relative] = (args.policy_root / relative).read_bytes()
        if getattr(args, 'without_frontier_offers', False):
            replacements[SCANNER] = ablate_frontier_offer(replacements[SCANNER],case)
        if getattr(args,'supplier_no_bid',False):
            relative=Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua')
            replacements[relative]=without_supplier_bid(replacements[relative],case)
        if getattr(args,'prototype_buyer',None):
            replacements[QUOTE_BRIDGE]=bypass_szeged_quote_screen(replacements[QUOTE_BRIDGE],case)
        if getattr(args,'seed_source_seats',False):
            relative=Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')
            replacements[relative],seat_provenance=seed_source_seats(replacements[relative],checkpoint,case)
    for relative, data in replacements.items():
        pins[csc][str(relative)] = dict(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
    # Recovery must match the exact staged production files, not the older
    # frozen carrier before those substitutions. No arbitrary package reuse.
    for source, destination in packages.items():
        if recovery:
            assert destination.is_dir() and manifest(destination) == pins[source]
            assert load(recovery / 'inputs.json')['packages'][source.name] == pins[source]
        else:
            assert not destination.exists()
    sys.path.insert(0, str(args.dependencies.resolve(strict=True)))
    import frida
    assert frida.__version__ == '17.24.3'
    assert Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve())
    out.mkdir(parents=True)
    write_json(out / 'inputs.json', dict(mode=args.mode, case=case,
        observePurchases=args.observe_purchases,
        observePurchaseLineage=getattr(args,'observe_purchase_lineage',False),
        observePurchaseExecution=getattr(args,'observe_purchase_execution',False),
        observePurchaseLifecycle=getattr(args,'observe_purchase_lifecycle',False),
        repairOwnedPurchase=getattr(args,'repair_owned_purchase',False),
        save_endpoint=getattr(args,'save_endpoint',False),
        supplier_no_bid=getattr(args,'supplier_no_bid',False),
        prototypeBuyer=getattr(args,'prototype_buyer',None),
        sourceSeatMigration=seat_provenance,
        without_frontier_offers=getattr(args,'without_frontier_offers',False),
        ablationScope=dict(player=case['player'],city=case['city'],districts=([36,37]if case_name=='nuremberg'else[case['district']]),
            plot=case['purchasePlots'][0]) if getattr(args,'without_frontier_offers',False) else None,
        through=args.through, save_sha256=case['sha256'],
        source_turn=source_turn,dependencies=str(args.dependencies.resolve()),frida_version=frida.__version__,
        source_policy_root=str(source_policy.resolve()) if case_name.startswith('nuremberg') else None,
        ownership_ce_dll=str(ownership_dll.resolve()) if ownership_dll else None,
        ce_sha256=effective_ce_sha, packages={source.name: value for source, value in pins.items()}))
    shutil.copyfile(Path(__file__), out / Path(__file__).name)
    (out / 'plot-watcher.lua').write_text(WATCHER.replace('__ENDPOINT__', str(args.through)).replace('__SCOPE__',lua(case)), encoding='utf-8')
    if recovery:
        shutil.copyfile(recovery / 'original-preferences.json', out / 'original-preferences.json')
    controller = make_probe_controller(out, user_root=user_root)
    controller.study_endpoint=args.through
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    installed = []
    observer = purchase_observer = attachment = None
    restore_allowed = False
    stream_errors = []

    def verify_packages():
        assert all(manifest(packages[source]) == pins[source] for source in installed)

    def stream_receipts(name):
        # Frida delivers bounded callback messages on its host thread. Each
        # append is flushed to disk before returning. A surviving journal is
        # explicitly partial evidence; only endpoint and closure receipts can
        # establish a completed replay. No console command is issued here.
        def receive(message, data):
            try:
                with (out / (name + '-live.ndjson')).open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(dict(partial=True, captured_unix=time.time(), message=message)) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
            except Exception as error:
                stream_errors.append(dict(observer=name, error=str(error), captured_unix=time.time()))
                # A full disk can also prevent this error receipt. Retain the
                # in-memory error so the replay cannot report complete below.
                try:
                    write_json(out / 'receipt-stream-errors.json', stream_errors)
                except OSError:
                    pass
        return receive

    try:
        for source, destination in packages.items():
            if not recovery:
                shutil.copytree(source, destination)
            installed.append(source)
        for relative, data in replacements.items():
            (packages[csc] / relative).write_bytes(data)
            (out / relative.name).write_bytes(data)
        if ownership_bytes:
            (packages[ce]/ce_relative).write_bytes(ownership_bytes)
        verify_packages()
        session.start(lambda: launch(SimpleNamespace(binary=binary), out))
        session.wait_context('MainMenu')
        if recovery:
            original = load(out / 'original-preferences.json')
            actual = flags(controller, 'inspect-interrupted-menu')
            assert entry_keys(actual) == entry_keys(original), 'Inventory changed since interrupted run'
            assert actual == original or {key for key, value in actual['mods'].items() if value} == test_ids
            restore_allowed = True
            configure(controller, out / 'recovered-setup', csc_id=ce_id)
        else:
            configure(controller, out, csc_id=ce_id)
            restore_allowed = True
        session.issue_once('enable-csc', f"""
local chosen
for _, m in ipairs(Modding.GetInstalledMods()) do
    if m.Id=='{csc_id}' then assert(not chosen); chosen=m end
end
assert(chosen and Modding.CanEnableMod(chosen.Handle)=='OK')
Modding.EnableMod(chosen.Handle,true)
""", 'MainMenu')
        assert {key for key, value in flags(controller, 'verify-local-pair')['mods'].items() if value} == test_ids
        session.issue_load_once(save, sha256=case['sha256'], native_directory=home / 'Saves/Single', turn=source_turn)

        plots = []

        def ready():
            verify_modules(session, (packages[ce] / ce_relative).resolve(), out, HOTFIX_SHA)
            if args.mode == 'integrated':
                qualify_integrated_policy(controller,out,case)
                if ownership_bytes:
                    raw=controller.cmd('''local s=assert(CE_AIDistrictPurchaseCompletionStatus())
print('CSC_OWNERSHIP_API_STATUS',s)
assert(s:match('"ready":1') and s:match('"faults":0'),'Ownership capability unavailable')
local status=assert(CE_AIDistrictScoresStatus())
local version=assert(tonumber(status:match('"version":(%d+)')))
local receipt=CE_AIDistrictPurchaseCompletionReceipt(version,'''+str(case['player'])+','+str(case['city'])+','+str(case['district'])+''')
print('CSC_OWNERSHIP_API_RECEIPT',receipt)
assert(receipt:match('"staged":'''+('0'if supplier_case else'1')+''''),'Unexpected main CSC ownership scope for this source')''',
                        'CSC_AI_BakersGameplay','qualify-main-ownership-api')
                    (out/'ownership-api-qualification.txt').write_text(raw,encoding='utf-8')
            if prepare_supplier:
                raw=controller.cmd(PREPARE_SUPPLIER,'CSC_AI_BakersGameplay','prepare-common-supplier-source')
                (out/'supplier-preparation.txt').write_text(raw,encoding='utf-8')
                assert re.search(r'CSC_SUPPLIER_RELEASED\s+216\s+861\s+',raw)
                write_json(out/'supplier-preparation.json',dict(verified=True,parent_save_sha256=case['sha256'],
                    released_plot=861,quarter_plot=788,turn=216,native_purchase=False,common_fixture=True))
            if supplier_case:
                raw=controller.cmd(INSPECT_SUPPLIER,'CSC_AI_BakersGameplay','inspect-supplier-chain')
                (out/'supplier-chain-qualification.txt').write_text(raw,encoding='utf-8')
            controller.cmd(read(out / 'plot-watcher.lua'), 'CSC_AI_BakersGameplay', 'watch-source-plots')
            raw = controller.cmd('local scope='+lua(case)+"""
local city=assert(CityManager.GetCity(scope.player,scope.city))
assert(city:GetName()==scope.name,'Wrong source city')
local center=assert(Map.GetPlot(city:GetX(),city:GetY()))
local indices={}
for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3)) do
    indices[#indices+1]=plot:GetIndex()
end
print('CSC_REPLAY_PLOTS=['..table.concat(indices,',')..']')
""", 'CSC_AI_BakersGameplay', 'scope-radius-three-plots')
            plots.extend(parse(raw, 'CSC_REPLAY_PLOTS'))
            assert len(plots) == len(set(plots)) and set(case['plots']) <= set(plots) and len(plots) <= 36
            if case_name=='nuremberg-supplier-follow':
                raw=controller.cmd('''local p=assert(Map.GetPlotByIndex(861));local city=assert(Cities.GetPlotPurchaseCity(p))
assert(p:GetOwner()==3 and city:GetID()==458758 and p:GetDistrictType()==-1 and p:GetImprovementType()==-1)
assert(p:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index)
print('CSC_SUPPLIER_OWNED_SOURCE',Game.GetCurrentGameTurn(),p:GetOwner(),city:GetID(),p:GetImprovementType())''',
                    'CSC_AI_BakersGameplay','qualify-paid-supplier-source')
                (out/'owned-supplier-qualification.txt').write_text(raw,encoding='utf-8')
            elif case_name=='nuremberg-reload':
                raw=controller.cmd('''local plot=assert(Map.GetPlotByIndex(788))
local city=assert(Cities.GetPlotPurchaseCity(plot))
assert(plot:GetOwner()==3 and city:GetID()==458758 and plot:GetDistrictType()==-1)
print('CSC_OWNERSHIP_RELOAD_SOURCE',Game.GetCurrentGameTurn(),plot:GetOwner(),city:GetID(),plot:GetDistrictType())''',
                    'CSC_AI_BakersGameplay','qualify-owned-reload-source')
                (out/'owned-reload-qualification.txt').write_text(raw,encoding='utf-8')
            elif case_name != 'nicopolis':
                qualify_purchase(controller,out,case,allow_tied=bool(getattr(args,'prototype_buyer',None)))
            return True

        session.ready_after_issue(source_turn, ('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay'), eligibility=ready)
        modules = load(out / 'loaded-modules.json')
        scope = dict(player=case['player'], city=case['city'], width=74, height=46, districtCount=38, district=case['district'],
            plots=sorted(plots), cePath=modules[DLL]['path'], streamRecords=True, traceTree=case_name!='nicopolis')
        if scope['traceTree']:
            # CE owns CheckForDistrict's entry detour. The existing observer's
            # threshold mode reads its untouched CityBuild caller instead;
            # no exclusion/repair treatment is enabled by this scope.
            scope['thresholdPlot']=case['purchasePlots'][0]
        write_json(out / 'scope.json', scope)
        sources = (STUDY / 'observer.js', HERE / 'dam_site_observer.js')
        for path in sources:
            shutil.copyfile(path, out / path.name)
        code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n"
        code += '\n'.join(read(out / path.name) for path in sources)
        attachment = frida.attach(session.owner.pid)
        observer = attachment.create_script(code)
        observer.on('message', stream_receipts('selector'))
        observer.load()
        assert observer.exports_sync.init(dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'],
            image_size=XP2_IMAGE_SIZE), scope)
        observer.exports_sync.advance()
        if args.observe_purchases:
            # Separate script with its own RPC state. Default is read-only.
            # Explicit buyer-prototype restrict mode can exclude a competing
            # city for the verified selected Quarter's contract. Prices/funds/
            # payment stay native; it never forces a district choice.
            purchase_sources = (STUDY / 'observer.js', HERE/'purchase_acknowledgement.js',
                HERE/'routine_supplier_observer.js',HERE / 'plot_purchase_observer.js')
            for path in purchase_sources[1:]:shutil.copyfile(path,out/path.name)
            purchase_code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n"
            purchase_code += '\n'.join(read(path) for path in purchase_sources)
            purchase_observer = attachment.create_script(purchase_code)
            purchase_observer.on('message', stream_receipts('purchase'))
            purchase_observer.load()
            # Other paid plots for this player serve as a natural positive
            # control for the command callbacks. Targeted savings observations
            # remain restricted to the two diagnostic footprints.
            purchase_scope = dict(player=case['player'], width=74, height=46, plots=case['purchasePlots'],
                allCommandPlots=True, streamRecords=True, city=case['city'],
                observeLineage=getattr(args,'observe_purchase_lineage',False),
                observeExecution=getattr(args,'observe_purchase_execution',False),
                observeLifecycle=getattr(args,'observe_purchase_lifecycle',False),
                observeRoutine=case_name=='nuremberg-supplier',
                repairOwnedPurchase=getattr(args,'repair_owned_purchase',False),
                prototypeBuyer=getattr(args,'prototype_buyer',None),district=case['district'],
                selectorObserverVerified=True) # init above verified the unpatched call/return window.
            write_json(out / 'purchase-scope.json', purchase_scope)
            assert purchase_observer.exports_sync.init(
                dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE),
                purchase_scope)
        controller.study_endpoint = args.through
        print('Purchase diagnostic armed', case_name, args.mode, flush=True)
        if args.through>source_turn:
            controller.play(args.through)
        trace = observer.exports_sync.freeze()
        write_json(out / 'selector-trace.json', trace)
        assert trace['fault'] is None and trace['active'] == 0
        if purchase_observer:
            purchase_trace = purchase_observer.exports_sync.freeze()
            write_json(out / 'purchase-trace.json', purchase_trace)
            assert purchase_trace['fault'] is None
            purchase_observer.unload()
            purchase_observer = None
        observer.unload()
        observer = None
        attachment.detach()
        attachment = None
        state = controller.state_read('replay-end')
        assert state['turn'] == args.through and not state['active']
        raw = controller.cmd('CSC_PURCHASE_Snapshot()', 'CSC_AI_BakersGameplay', 'endpoint-readback')
        (out / 'endpoint-plots.txt').write_text(raw, encoding='utf-8')
        if getattr(args,'save_endpoint',False):
            # Preserve the paused endpoint, with native SaveComplete and the
            # shared controller's phase checks. Rotating autoplay saves are
            # useful backups but do not qualify a later exact-boundary replay.
            checkpoint=save_inactive_boundary(controller,turn=args.through,name='CSC_PURCHASE_FOLLOWTHROUGH',
                native_directory=home/'Saves/Single',archive=out/'endpoint.Civ6Save')
            write_json(out/'endpoint-checkpoint.json',checkpoint)
        for name in LOGS:
            source=user_root / 'Logs' / name
            # A zero-turn source preparation may create no native AI logs.
            # Outcome runs still require every log; never hide a missing trace.
            if prepare_supplier and not source.exists():
                write_json(out/('absent-'+name+'.json'),dict(turns_advanced=0,reason='No AI activation during source preparation'))
            else:
                shutil.copyfile(source, out / name)
    except Exception as error:
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        # A timeout must retain whatever the native callbacks already saw.
        # Cleanup faults must also leave the shared controller an opportunity
        # to restore preferences and release its exclusively owned process.
        cleanup_errors = []
        for name, script in (('purchase', purchase_observer), ('selector', observer)):
            if script:
                try:
                    write_json(out / (name + '-partial-trace.json'), script.exports_sync.freeze())
                except Exception as error:
                    cleanup_errors.append(dict(operation=name + '-freeze', error=str(error)))
                try:
                    script.unload()
                except Exception as error:
                    cleanup_errors.append(dict(operation=name + '-unload', error=str(error)))
        if attachment:
            try:
                attachment.detach()
            except Exception as error:
                cleanup_errors.append(dict(operation='detach', error=str(error)))
        if cleanup_errors:
            write_json(out / 'observer-cleanup-errors.json', cleanup_errors)
        if session.owner is not None and session.owner.poll() is None:
            # configure saves preferences before its first mutation. Recover
            # that snapshot even when later configuration checks fail.
            restore_allowed = restore_allowed or not recovery and (out / 'original-preferences.json').exists()
            session.close(restore_preferences=lambda: restore_preferences(controller, out) if restore_allowed else None,
                restore_package=verify_packages)
        if session.closed and restore_allowed:
            for source in installed:
                packages[source].rename(out / source.name)
        if cleanup_errors and sys.exc_info()[0] is None:
            raise RuntimeError('Observer cleanup failed; see observer-cleanup-errors.json')
    assert session.closed, 'Endpoint captured without verified shared-session closure'
    assert not stream_errors, 'Native receipt stream failed; partial evidence only'
    write_json(out / 'complete.json', dict(verified=True, turns_advanced=args.through-source_turn))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save-endpoint',action='store_true',help='Preserve one verified inactive endpoint checkpoint')
    parser.add_argument('--supplier-no-bid',action='store_true',help='Diagnostic supplier case only: keep mapped allowances/protection but remove its exact positive bid')
    parser.add_argument('--mode', choices=('original', 'frontier', 'integrated'), required=True)
    parser.add_argument('--case',choices=tuple(CASES),default='nicopolis')
    parser.add_argument('--without-frontier-offers',action='store_true',
        help='Diagnostic ablation of the exact fixture pair only; other frontier offers remain active')
    for name in ('output', 'reference', 'checkpoint', 'my-games', 'user-root', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--recover-from', type=Path)
    parser.add_argument('--original-run', type=Path)
    parser.add_argument('--policy-root', type=Path)
    parser.add_argument('--source-policy-root',type=Path,help='Historical main files matching the source ledger; current policy is staged separately')
    parser.add_argument('--ownership-ce-dll',type=Path,help='Explicit supported-build CE DLL for main ownership API validation')
    parser.add_argument('--ownership-ce-sha',help='Exact SHA256 pin for that integrated CE build')
    parser.add_argument('--through', type=int, default=208)
    parser.add_argument('--observe-purchases', action='store_true')
    parser.add_argument('--repair-owned-purchase',action='store_true',
        help='Diagnostic only: acknowledge a measured paid purchase after fresh intended-city ownership checks')
    parser.add_argument('--observe-purchase-lifecycle',action='store_true',
        help='Read-only known contract status/dispatch, Economic eligibility and decorator state; requires lineage')
    parser.add_argument('--observe-purchase-lineage',action='store_true',
        help='Read-only tree/contract creation links; requires --observe-purchases')
    parser.add_argument('--observe-purchase-execution',action='store_true',
        help='Read-only request/admission/dispatch and acquisition-caller receipts; requires --observe-purchases')
    parser.add_argument('--prototype-buyer',choices=('observe','restrict'),
        help='Szeged diagnostic only: allow its tied quote; restrict mode can exclude other native buyers')
    parser.add_argument('--seed-source-seats',action='store_true',
        help='Diagnostic Szeged fixture only: seed absent seat properties from pinned turn-1 records')
    options = parser.parse_args()
    if options.supplier_no_bid and (options.case!='nuremberg-supplier' or options.mode!='integrated'):
        parser.error('Supplier ablation requires the explicit integrated supplier case')
    if options.ownership_ce_dll and (not options.case.startswith('nuremberg') or options.mode!='integrated'
            or not options.ownership_ce_sha or options.repair_owned_purchase or options.prototype_buyer
            or options.without_frontier_offers or not options.source_policy_root):
        parser.error('integrated ownership validation requires full main Nuremberg, historical source policy and explicit CE pin; no external treatment')
    if options.case=='nuremberg-reload'and not options.ownership_ce_dll:
        parser.error('retained-plan reload requires the explicitly qualified integrated ownership CE build')
    if options.repair_owned_purchase and (options.case!='nuremberg' or options.mode!='integrated'
            or not options.observe_purchase_lifecycle or not options.observe_purchase_execution
            or not options.observe_purchases or not options.observe_purchase_lineage
            or options.without_frontier_offers):
        parser.error('paid acknowledgement prototype requires full integrated Nuremberg with lifecycle/execution/lineage observations')
    if options.observe_purchase_lifecycle and not(options.observe_purchases and options.observe_purchase_lineage):
        parser.error('lifecycle observation requires purchase and lineage observation')
    if options.case == 'nicopolis' and options.mode != 'original' and not options.original_run:
        parser.error('non-original modes require --original-run')
    if options.mode == 'integrated' and not options.policy_root:
        parser.error('integrated requires --policy-root')
    if options.case != 'nicopolis' and options.mode != 'integrated':
        parser.error('new purchase fixtures require the integrated main CSC policy')
    if options.without_frontier_offers and options.mode != 'integrated':
        parser.error('positive-frontier ablation requires integrated mode')
    if options.observe_purchase_lineage and not options.observe_purchases:
        parser.error('lineage observation requires --observe-purchases')
    if options.observe_purchase_execution and not options.observe_purchases:
        parser.error('execution observation requires --observe-purchases')
    if options.prototype_buyer and (options.case!='szeged' or options.mode!='integrated'
            or not options.observe_purchases or not options.observe_purchase_lineage):
        parser.error('buyer prototype requires integrated Szeged with purchase and lineage observation')
    if options.prototype_buyer and options.without_frontier_offers:
        parser.error('buyer comparison requires the same active offer in both arms; do not ablate it')
    if options.seed_source_seats and (options.case!='szeged' or options.mode!='integrated'):
        parser.error('source-seat migration is qualified only for integrated Szeged')
    run(options)
