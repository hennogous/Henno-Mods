"""Live native observation and zero-progress placement adapter, no own transport."""
from dataclasses import replace,asdict
import json,re,time
from pathlib import Path
from .policy import Budget,PROFILES
from .needs import from_observations
from .observations import build_candidates
from .metrics import summarize

def parse(raw,marker):
    return json.loads(re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)[-1])

class NativeAdapter:
    def __init__(self,runner,root,write,lua,*,material_first=False,stepwise=False,connector_limit=0):
        self.r=runner;self.root=Path(root);self.write=write;self.lua=lua
        self.cities={};self.players={};self.turn=None;self.current={};self.placements=0
        self.material_first=material_first;self.stepwise=stepwise;self.connector_limit=connector_limit
        self.planner=None
        self.delta_mode=False

    def collect(self,turn,*,quarters=None):
        previous_cities=self.cities
        force_delta=getattr(self,'_last_collect_turn',None)==turn
        self.turn=turn
        if self.material_first:venues={'turn':turn,'venues':[]}
        else:
            raw=self.r.cmd(Path(__file__).with_name('native_venues.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','exact-service-venues-'+str(turn))
            venues=parse(raw,'CSC_SERVICE_VENUES');assert venues['turn']==turn
        provided_quarters=quarters is not None
        quarters=quarters or {'turn':turn,'cities':{}}
        if self.stepwise and not provided_quarters:
            raw=self.r.cmd(Path(__file__).with_name('native_quarter_sites.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','current-quarter-sites-'+str(turn))
            quarters=parse(raw,'CSC_QUARTER_SITES');assert quarters['turn']==turn
        watches={}
        if self.material_first and self.planner is not None:
            for (pid,cid),marked in self.planner.cache.items():
                if self.planner.wide_due(pid,cid,turn):continue
                previous=self.cities.get((pid,cid),{});tiles={p['index']:p for p in previous.get('tiles',())}
                indices=set()
                for c in marked:
                    indices.add(c.plot);indices.update(c.material_plots);indices.update(c.missing_tiles)
                    for i in c.missing_tiles:indices.update(tiles.get(i,{}).get('neighbors',()))
                    indices.update(tiles.get(c.plot,{}).get('neighbors',()))
                for site in quarters['cities'].get(f'{pid}:{cid}',[]):
                    indices.add(site['plot']);indices.update(site['neighbors'])
                watches[f'{pid}:{cid}']={i:True for i in indices}
        code='CSC_SERVICE_NATIVE.delta_mode='+str(self.delta_mode).lower()+';CSC_SERVICE_NATIVE.delta_force_refresh='+str(force_delta).lower()+';CSC_SERVICE_NATIVE.external_quarters='+self.lua(quarters['cities'])+';CSC_SERVICE_NATIVE.quarters_turn='+str(turn)+';CSC_SERVICE_NATIVE.material_first='+str(self.material_first).lower()+';CSC_SERVICE_NATIVE.city_watch='+self.lua(watches)+';CSC_SERVICE_NATIVE.external_venues='+self.lua(venues['venues'])+';CSC_SERVICE_NATIVE.venues_turn='+str(turn)+';CSC_SERVICE_NATIVE.Read();'
        data=parse(self.r.cmd(code,'PlotInfo','service-read-'+str(turn)),'CSC_SERVICE_NATIVE')
        assert abs(data['turn']-turn)<=1,'Unexpected UI/Core phase'
        self.write(self.root/('native-service-deltas'if self.delta_mode else'native-service')/f'turn-{turn:03d}.json',data)
        self.data=data;self.cities={(x['player'],x['city']):x for x in data['cities']}
        # Opt-in delta reader returns references for unchanged fixed scopes.
        # Missing references fail, rather than silently dropping opportunities.
        for row in data.get('unchanged',[]):
            key=row['player'],row['city'];assert key in previous_cities,'Unknown delta scope'
            self.cities[key]=dict(previous_cities[key],turn=turn,broad_scan=False,delta_reused=True)
        if getattr(self,'delta_mode',False):
            for row in data['cities']:
                row['delta_full_read_turn']=turn
                key=row['player'],row['city']
                if self.planner is not None:
                    # Cache and timestamp are one invariant in Planner.wide_due.
                    # Invalidate both after a changed native scope.
                    self.planner.cache.pop(key,None);self.planner.scan_turn.pop(key,None)
        self.players={x['player']:x for x in data['players']};self.current={}
        for key,city in self.cities.items():
            # Keep raw UI clocks, but attach the independently read Core anchor.
            obs=dict(city,turn=turn);obs['readiness']={}
            if getattr(self,'delta_mode',False)and city.get('delta_reused')and key in getattr(self,'candidate_cache',{}):
                self.current[key]={k:replace(c,observed_turn=turn)for k,c in self.candidate_cache[key].items()}
            else:self.current[key]=self.candidates(obs)
        self.candidate_cache=dict(self.current)
        self._last_collect_turn=turn
        if self.delta_mode:
            # Keep the existing complete file schema for reports, alongside the
            # raw delta references and explicit age of each full observation.
            self.data=dict(data,cities=list(self.cities.values()),delta_mode=True)
            self.write(self.root/'native-service'/f'turn-{turn:03d}.json',self.data)
        if self.material_first:
            self.write(self.root/'opportunity-catalogue'/f'turn-{turn:03d}.json',
                {'turn':turn,'broad_cities':[{'player':pid,'city':cid,'candidates':[asdict(c)for c in self.current[pid,cid].values()]}for (pid,cid),city in self.cities.items()if city.get('broad_scan')],
                 'treasury':data['players'],'native_rejections':[{'player':x['player'],'city':x['city'],'district_state':x.get('district_state')}for x in data['cities']],
                 'native_purchase_targets':[{'player':x['player'],'city':x['city'],'listed':x.get('native_purchase_target_list',[]),'approved':x.get('native_purchase_approved',[]),'command_approved':x.get('native_purchase_command_approved',[]),'query_kind':x.get('native_purchase_query_kind')}for x in data['cities']]})
        return data

    def record_chain_metrics(self,turn,*,value=None):
        if value is None:
            raw=self.r.cmd(Path(__file__).with_name('native_chain_metrics.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','chain-metrics-'+str(turn))
            value=parse(raw,'CSC_CHAIN_METRICS')
        assert value['turn']==turn and not value['errors']
        value['treasury_cashflow']={'source':'same-boundary UI treasury: gross minus total maintenance','players':list(self.players.values())}
        self.write(self.root/'chain-metrics'/f'turn-{turn:03d}.json',value)
        self.write(self.root/'metric-points'/f'turn-{turn:03d}.json',summarize(value))
        return value

    def candidates(self,obs):
        out=[];tiles={x['index']:x for x in obs['tiles']}
        for c in build_candidates(obs,material_first=self.material_first,stepwise=self.stepwise,connector_limit=self.connector_limit):
            if c.service:
                profile=PROFILES[c.service];raw=tiles[c.plot]['chain'][c.quarter]
                chain=raw[str(profile.stage)]if isinstance(raw,dict)else raw[profile.stage-1]
                civic=self.cities[c.player,c.city]['readiness']
                ready=isinstance(civic,dict)and civic.get(profile.civic,False)
                supplied=[tiles[i]for i in c.material_plots if i in tiles and tiles[i]['improvement']>=0 and not tiles[i]['improvement_pillaged']]
                improved_base=any(c.quarter in x['base_for']for x in supplied)
                improved_spec=any(c.quarter in x['spec_for']for x in supplied)
                setup=improved_base and(not profile.requires_specialty or improved_spec)
                c=replace(c,research_ready=ready,producer_ready=chain['ready'],
                          ready_in_turns=chain['turns']if ready and setup else 999,confidence=.8 if chain['ready']and ready and setup else .5)
            out.append(c)
        return {c.key:c for c in out}

    def wide_candidates(self,pid,cid,turn):return tuple(self.current[pid,cid].values())
    def refresh(self,c):return self.current.get((c.player,c.city),{}).get(c.key)
    def needs(self,pid,cid):
        if self.material_first:return {}
        c=self.cities[pid,cid]
        return from_observations(population=c['population'],food_surplus=c.get('food_surplus'),
            housing_shortfall=max(0,c['population']-c['housing'])if c.get('housing')is not None else 0,
            naval_unit_in_production=c['naval_unit_in_production'],
            culture_emphasis=c['culture_emphasis'],religion_emphasis=c['religion_emphasis'])
    def budget(self,pid):
        p=self.players[pid]
        maintenance=p.get('maintenance',0)
        return Budget(p['gold'],p.get('net_income',0),emergency_reserve=__import__('math').ceil(2*maintenance)if self.stepwise else 0,maintenance=maintenance,cashflow_observed=p.get('cashflow_observed',False))
    def purchase_facts(self,c):
        self.collect(self.turn);fresh=self.refresh(c);assert fresh is not None
        param=self.data.get('purchase_parameter')
        # No guessed fixture parameter or ownership/gold substitute.
        assert param is True,'Native boolean plot-purchase parameter unavailable'
        venue=None
        if fresh.service:
            venue=next(x['type']for x in self.cities[c.player,c.city]['venues']if x['plot']==c.customer_plot and x['type']in PROFILES[c.service].venues)
        return fresh,self.budget(c.player),self.turn,param,venue
    def purchase_readback(self,e):
        code='local p=Players['+str(e['player'])+'];local c=CityManager.GetCity('+str(e['player'])+','+str(e['city'])+');print("CSC_PURCHASE_READBACK="..CSC_SERVICE_NATIVE.Json({city_owner=c and c:GetOwner()or -1,plot_owner=Map.GetPlotByIndex('+str(e['purchase_plot'])+'):GetOwner(),gold=p:GetTreasury():GetGoldBalance(),turn=Game.GetCurrentGameTurn()}));'
        return parse(self.r.cmd(code,'PlotInfo','purchase-real-gold-readback'),'CSC_PURCHASE_READBACK')
    def place_zero(self,c):
        defs=self.cities[c.player,c.city]['district_defs'][c.quarter]
        target={'player':c.player,'city':c.city,'plot':c.plot,'quarter':c.quarter,'districtHash':defs['Hash'],'districtIndex':defs['Index']}
        tag=f'{self.turn}-{c.player}-{c.city}-{c.quarter}'
        folder=self.root/'placements'/tag
        # Delegate to the maintained planner after Service policy has selected a
        # single site; its old material ranking cannot replace the selected site.
        self.r.cmd('CSC_FOUNDATION_PROBE.Plan({'+self.lua(target)+'});CSC_FOUNDATION_PROBE.Export();','CSC_AdjacencyGameplay','service-plan-'+tag)
        planned=parse(self.r.cmd('CSC_FOUNDATION_PROBE.Export();','CSC_AdjacencyGameplay','service-plan-proof-'+tag),'CSC_FOUNDATION_EXPORT')['plan']
        assert len(planned)==1 and planned[0]['plot']==c.plot
        exact='local t='+self.lua(target)+''';local city=assert(CityManager.GetCity(t.player,t.city));local q=city:GetBuildQueue();assert(not q:HasBeenPlaced(t.districtHash));local producible=q:CanProduce(t.districtHash,false,true);assert(producible,'District no longer producible');local p=Map.GetPlotByIndex(t.plot);local a={};a[CityOperationTypes.PARAM_DISTRICT_TYPE]=t.districtHash;local found=false;local result=CityManager.GetOperationTargets(city,CityOperationTypes.BUILD,a);for _,idx in ipairs(result and result[CityOperationResults.PLOTS]or {})do if idx==t.plot then found=true end end;a[CityOperationTypes.PARAM_X]=p:GetX();a[CityOperationTypes.PARAM_Y]=p:GetY();local exact=CityManager.CanStartOperation(city,CityOperationTypes.BUILD,a,true);print('CSC_SERVICE_SITE_PREFLIGHT',t.player,t.city,t.plot,found,exact);assert(found and exact,'Selected site no longer native-legal');'''
        def ui(reason,pre=False):
            raw=self.r.cmd((exact if pre else '')+'CSC_FOUNDATION_UI.targets={'+self.lua(target)+'};CSC_FOUNDATION_UI.Capture('+json.dumps(reason)+');CSC_FOUNDATION_UI.Export();','PlotInfo','ui-'+reason)
            data=parse(raw,'CSC_FOUNDATION_UI');assert not data['errors']
            rows=[x for x in data['history']if x['reason']==reason];assert len(rows)==1
            assert abs(rows[0]['turn']-self.turn)<=1
            return rows[0]
        before=ui('before-'+tag,True)
        assert before['progress']==0 and before['cost']>0 and not before['has_been_placed']
        self.r.cmd('assert(Game.GetCurrentGameTurn()=='+str(self.turn)+' and not AutoplayManager.IsActive());','GameCore_Tuner','safe-commit-'+tag)
        self.r.cmd('CSC_FOUNDATION_PROBE.Commit();','CSC_AdjacencyGameplay','zero-commit-'+tag)
        after=ui('after-'+tag)
        g,_=self.r.capture('verified-'+tag);native=g['targets'][-1]['after']
        queues=all(before.get(k)==after.get(k)for k in('queue_size','queue','current_hash'))
        proof={'verified':True,'owner':native['owner'],'plot':c.plot,'quarter':c.quarter,
            'progress_before':before['progress'],'progress_after':after['progress'],
            'cost_before':before['cost'],'cost_after':after['cost'],
            'native_incomplete':native['district_present']and not native['complete']and native['district_type']==defs['Index'],
            'queue_unchanged':queues}
        self.write(folder/'validation.json',{'proof':proof,'candidate':asdict(c),'before':before,'after':after,'native':native})
        assert after['has_been_placed']and after['progress']==0 and before['cost']==after['cost']and queues
        self.placements+=1
        # Refresh same-type exclusion after this commitment before another cycle.
        self.collect(self.turn)
        return proof
