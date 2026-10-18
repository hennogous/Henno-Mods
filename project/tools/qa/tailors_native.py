"""Report-only Tailors native matrix. Assertion failures do not stop later cases.
Run only after tailors_world.lua fixture creation in a disposable game.
"""
import argparse
import json
from pathlib import Path
import sys
import time
from csc_qa import Run, ROOT, tuner

W='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'
T='BUILDING_CSC_TAILORS_TAILOR'
F='BUILDING_CSC_TAILORS_FASHION_HOUSE'
S2='BUILDING_CSC_TAILORS_STAGE_2_SERVICE'
S3='BUILDING_CSC_TAILORS_STAGE_3_SERVICE'
S4='BUILDING_CSC_TAILORS_STAGE_4_SERVICE'


class Matrix:
    def __init__(self, output):
        self.run=Run(output)
        self.cases=[]
    def drain(self):
        states=tuner.states()
        for cycle in range(6):
            closed=False
            for name in ('CreateCorporationPopup','WonderBuiltPopup','TechCivicCompletedPopup','NaturalWonderPopup'):
                if name not in states:continue
                code="if not ContextPtr:IsHidden() then if type(OnClose)=='function' then OnClose();print('TQA_POPUP_CLOSED');else print('TQA_UNHANDLED_POPUP');end end"
                messages=tuner.command(code,states[name],.2)
                if any('TQA_UNHANDLED_POPUP' in x or 'ERR:' in x for x in messages):raise RuntimeError('Unhandled popup '+name)
                if any('TQA_POPUP_CLOSED' in x for x in messages):
                    closed=True
                    with (self.run.output/'popup-drain.txt').open('a',encoding='utf-8') as f:f.write(name+'\n'+'\n'.join(messages)+'\n')
            if not closed:break
    def command(self,name,code,state='CSC_AdjacencyGameplay',check=False):
        try:
            self.run.execute(name,code,state,wait=.7,allow_event_errors=True)
            if not check and state=='CSC_AdjacencyGameplay' and any(trigger in code for trigger in ('IMPROVEMENT_CORPORATION', 'TQA.Civic(', 'TQA.Tech(', 'BUILDING_BOLSHOI', 'BUILDING_BROADWAY', 'BUILDING_SYDNEY')):self.drain()
            status='passed'
        except RuntimeError:
            status='failed'
        self.cases.append({'name':name,'kind':'assertion' if check else 'setup','status':status,'evidence':self.run.results['checks'][-1]['evidence'], 'event_runtime_errors':self.run.results['checks'][-1].get('event_runtime_errors',0)})
        (self.run.output/'matrix.json').write_text(json.dumps(self.cases,indent=2))
        if status=='failed' and not check: raise RuntimeError('Setup failed: '+name)
        return status=='passed'
    def check(self,name,code,state='PlotInfo'):
        # UI has a mirrored game state. Retain early samples, then classify the
        # final observation after a bounded settle window; never retry mutations.
        for attempt in range(4):
            label=name if attempt==0 else name+f' settled sample {attempt}'
            if self.command(label,code,state,True):return True
            if attempt<3:time.sleep(1)
        return False
    def by(self,name,city,building,yield_name,value):
        return self.check(name,f'TQA.Equal({json.dumps(name)},TQA.BY("{city}","{building}","YIELD_{yield_name}"),{value});')


def material_local(m):
    m.command('prepare material-local source and empty inputs',f"TQA.Add('QA','{W}');TQA.Remove('A','{T}');TQA.Remove('A','{F}');TQA.Remove('A','BUILDING_LIGHTHOUSE');TQA.Resource('MA1',nil,nil);TQA.Resource('MA2',nil,nil);TQA.Resource('MA3',nil,nil);")
    m.by('empty Workshop Culture','A',W,'CULTURE',0)
    m.command('unimproved Cotton','TQA.Resource("MA1","RESOURCE_COTTON",nil)')
    m.by('unimproved Base gives no Workshop Culture','A',W,'CULTURE',0)
    m.command('improve Cotton','TQA.Resource("MA1","RESOURCE_COTTON","IMPROVEMENT_PLANTATION")')
    m.by('improved Base gives one Workshop Culture','A',W,'CULTURE',1)
    m.command('second improved Base','TQA.Resource("MA2","RESOURCE_CSC_FLAX","IMPROVEMENT_FARM")')
    m.by('two Base improvements stack Workshop Culture','A',W,'CULTURE',2)
    m.command('Specialty does not supply Workshop','TQA.Resource("MA3","RESOURCE_DYES","IMPROVEMENT_PLANTATION")')
    m.by('Specialty leaves Workshop Culture unchanged','A',W,'CULTURE',2)
    m.command('Base Industry','TQA.Resource("MA1","RESOURCE_COTTON","IMPROVEMENT_INDUSTRY")')
    m.by('Industry Base total two plus ordinary one','A',W,'CULTURE',3)
    m.command('Base Corporation','TQA.Resource("MA1","RESOURCE_COTTON","IMPROVEMENT_CORPORATION")')
    m.by('Corporation Base total three plus ordinary one','A',W,'CULTURE',4)
    m.command('restore ordinary Base','TQA.Resource("MA1","RESOURCE_COTTON","IMPROVEMENT_PLANTATION")')
    m.command('local Tailor','TQA.Add("QA","'+T+'")')
    m.by('local Tailor returns Production to Workshop','A',W,'PRODUCTION',1)
    m.by('local Tailor returns Gold to Workshop','A',W,'GOLD',1)
    m.by('Workshop supplies local Tailor Culture','A',T,'CULTURE',1)
    m.command('local Fashion House','TQA.Add("QA","'+F+'")')
    m.by('Tailor and Fashion House Production stack','A',W,'PRODUCTION',2)
    m.by('Tailor and Fashion House Gold stack','A',W,'GOLD',2)
    m.by('Fashion House local and Specialty Culture','A',F,'CULTURE',2)
    m.command('Specialty Industry','TQA.Resource("MA3","RESOURCE_DYES","IMPROVEMENT_INDUSTRY")')
    m.by('Fashion House Specialty Industry total plus local','A',F,'CULTURE',3)
    m.command('Specialty Corporation','TQA.Resource("MA3","RESOURCE_DYES","IMPROVEMENT_CORPORATION")')
    m.by('Fashion House Specialty Corporation total plus local','A',F,'CULTURE',4)
    m.command('Specialty ordinary restored','TQA.Resource("MA3","RESOURCE_DYES","IMPROVEMENT_PLANTATION")')
    m.command('remove one local stage','TQA.Remove("A","'+T+'")')
    m.by('only removed stage return stops','A',W,'PRODUCTION',1)
    m.command('restore local Tailor','TQA.Add("QA","'+T+'")')
    m.command('local Lighthouse','TQA.Add("HA","BUILDING_LIGHTHOUSE")')
    m.by('Lighthouse return stacks with local stages','A',W,'PRODUCTION',3)
    m.by('Lighthouse Gold return stacks','A',W,'GOLD',3)
    m.by('Workshop gives Lighthouse Production','A','BUILDING_LIGHTHOUSE','PRODUCTION',1)


def stage3(m):
    m.command('prepare Stage 3 customers','TQA.Add("QB","'+W+'");TQA.Add("MC","BUILDING_MARKET");TQA.Add("SC","BUILDING_SHRINE");TQA.Add("SC","BUILDING_TEMPLE");')
    for pop in (1,5,10):
        m.command(f'Stage 3 population {pop} baseline','TQA.Remove("B","'+T+'");TQA.Pop("C",'+str(pop)+');')
        m.command(f'capture Stage 3 population {pop}', '''TQA.Mem={};for _,c in ipairs({'B','C'}) do for _,y in ipairs({'CULTURE','PRODUCTION','GOLD'}) do TQA.Mem[c..y]=TQA.Raw(c,'YIELD_'..y);end;end;''','PlotInfo')
        m.command(f'Stage 3 population {pop} active','TQA.Add("QB","'+T+'")')
        for c,y,expected in [('C','CULTURE',.2*pop),('B','PRODUCTION',1+.2*pop),('B','GOLD',1+.2*pop)]:
            m.check(f'Stage3 two customer families pop {pop} {c} {y}',f'TQA.Equal("Stage3 {c} {y}",TQA.Raw("{c}","YIELD_{y}")-TQA.Mem["{c}{y}"],{expected},.06);')
    m.command('Stage3 mixed customer baseline','TQA.Remove("B","'+T+'");TQA.Pop("C",10);TQA.Pop("F",6);TQA.Add("MF","BUILDING_MARKET");')
    m.command('capture Stage3 mixed customers', '''TQA.Mem={};for _,c in ipairs({'B','C','F'}) do for _,y in ipairs({'CULTURE','PRODUCTION','GOLD'}) do TQA.Mem[c..y]=TQA.Raw(c,'YIELD_'..y);end;end;''','PlotInfo')
    m.command('activate Stage3 mixed customers','TQA.Add("QB","'+T+'")')
    for c,y,v in [('C','CULTURE',2),('F','CULTURE',.6),('B','PRODUCTION',3.6),('B','GOLD',3.6)]:
        m.check(f'Stage3 mixed {c} {y}',f'TQA.Equal("mixed {c} {y}",TQA.Raw("{c}","YIELD_{y}")-TQA.Mem["{c}{y}"],{v},.08);')
    m.command('pillage one Stage3 customer','TQA.Pillage("C","BUILDING_TEMPLE",true)')
    m.check('Stage3 pillaged Temple loses only its return','TQA.Equal("pillage return",TQA.Raw("B","YIELD_PRODUCTION")-TQA.Mem.BPRODUCTION,2.6,.07);')
    m.command('repair Stage3 customer','TQA.Pillage("C","BUILDING_TEMPLE",false)')
    m.check('Stage3 repaired Temple restores return','TQA.Equal("repair return",TQA.Raw("B","YIELD_PRODUCTION")-TQA.Mem.BPRODUCTION,3.6,.08);')


def stage4(m):
    m.command('prepare Stage4 seller and Amphitheater','TQA.Add("QD","'+W+'");TQA.Add("TE","BUILDING_AMPHITHEATER");TQA.Add("QD","'+F+'");')
    for pop in (4,5,9,10,55):
        m.command(f'Stage4 customer population {pop}',f'TQA.Pop("E",{pop})')
        stacks=pop//5
        m.by(f'Stage4 pop {pop} seller Production four sites','D',F,'PRODUCTION',4*stacks)
        m.by(f'Stage4 pop {pop} seller Gold four sites','D',F,'GOLD',4*stacks)
        for building in ('BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE'):
            # Amphitheater native intrinsic Culture is 2; Bolshoi 2; other two 0.
            intrinsic=2 if building in ('BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE') else 0
            m.by(f'Stage4 pop {pop} {building}','E',building,'CULTURE',intrinsic+stacks)
    m.command('unequal population customer low','TQA.Pop("D",15);TQA.Pop("E",5)')
    m.by('producer fifteen customer five uses customer demand','D',F,'PRODUCTION',4)
    m.command('unequal population customer high','TQA.Pop("D",5);TQA.Pop("E",15)')
    m.by('producer five customer fifteen uses customer demand','D',F,'PRODUCTION',12)
    m.command('pillage Stage4 seller','TQA.Pillage("D","'+F+'",true)')
    m.by('pillaged seller clears customer Culture','E','BUILDING_AMPHITHEATER','CULTURE',2)
    m.command('repair Stage4 seller','TQA.Pillage("D","'+F+'",false)')
    m.by('repaired seller restores customer Culture','E','BUILDING_AMPHITHEATER','CULTURE',5)
    m.command('pillage Stage4 Wonder customer','TQA.Pillage("E","BUILDING_BROADWAY",true)')
    m.by('one pillaged site removes only three stacks','D',F,'PRODUCTION',9)
    m.command('repair Stage4 Wonder','TQA.Pillage("E","BUILDING_BROADWAY",false)')
    m.by('Wonder repair restores independent site','D',F,'PRODUCTION',12)


def stage4_baselined(m):
    buildings=('BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE')
    m.command('Stage4 independent baseline remove source','TQA.Remove("D","'+F+'")')
    m.command('capture actual vanilla venue baselines', '''TQA.VenueBase={};for _,b in ipairs({'BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE'}) do TQA.VenueBase[b]=TQA.BY('E',b,'YIELD_CULTURE');print('VENUE_BASE',b,TQA.VenueBase[b]);end''','PlotInfo')
    m.command('Stage4 independent source restored','TQA.Add("QD","'+F+'")')
    for pop in (4,5,9,10,55):
        m.command(f'baselined customer population {pop}',f'TQA.Pop("E",{pop})')
        m.by(f'baselined Stage4 seller pop {pop}','D',F,'PRODUCTION',4*(pop//5))
        for b in buildings:m.check(f'baselined Stage4 {pop} {b}',f'TQA.Equal("Culture delta",TQA.BY("E","{b}","YIELD_CULTURE")-TQA.VenueBase["{b}"],{pop//5});')
    m.command('Stage4 final customer population ten','TQA.Pop("E",10)')
    m.command('baselined pillage seller',f'TQA.Pillage("D","{F}",true)')
    m.check('baselined pillaged seller clears customer',"TQA.Equal('seller pillage',TQA.BY('E','BUILDING_AMPHITHEATER','YIELD_CULTURE')-TQA.VenueBase.BUILDING_AMPHITHEATER,0);")
    m.command('baselined repair seller',f'TQA.Pillage("D","{F}",false)')
    m.check('baselined repaired seller restores customer',"TQA.Equal('seller repair',TQA.BY('E','BUILDING_AMPHITHEATER','YIELD_CULTURE')-TQA.VenueBase.BUILDING_AMPHITHEATER,2);")
    m.command('baselined pillage Broadway',"TQA.Pillage('E','BUILDING_BROADWAY',true)")
    m.by('baselined pillaged site removes only its return','D',F,'PRODUCTION',6)
    m.command('baselined repair Broadway',"TQA.Pillage('E','BUILDING_BROADWAY',false)")
    m.by('baselined repaired site restores return','D',F,'PRODUCTION',8)


def services(m):
    # A supplies conventional Harbor/Holy Site/Theater customers; D supplies all
    # four performance venues. Native GPP/Tourism measurements, not source flags.
    m.check('Dockmaster absent before civic',f'TQA.Service("A","{S2}",false)')
    m.command('capture base Admiral points',"TQA.AdmBase=TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL');",'PlotInfo')
    m.command('unlock Naval Tradition',"TQA.Civic('CIVIC_NAVAL_TRADITION',true)")
    m.check('Dockmaster established by all prerequisites',f'TQA.Service("A","{S2}",true)')
    m.check('one Dockmaster grants one Admiral point',"TQA.Equal('Admiral delta',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.AdmBase,1);")
    m.command('remove all Base improvements',"TQA.Resource('MA1','RESOURCE_COTTON',nil);TQA.Resource('MA2','RESOURCE_CSC_FLAX',nil);")
    m.check('unsupplied Dockmaster retains established building',f'TQA.Service("A","{S2}",true)')
    m.check('unsupplied Dockmaster deactivates Admiral point',"TQA.Equal('Admiral supply gate',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.AdmBase,0);")
    m.command('restore a Base improvement',"TQA.Resource('MA1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION')")
    m.check('restored supply reactivates Dockmaster',"TQA.Equal('Admiral restoration',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.AdmBase,1);")
    m.command('pillage Lighthouse',"TQA.Pillage('A','BUILDING_LIGHTHOUSE',true)")
    m.check('pillaged customer disables Dockmaster',"TQA.Equal('Lighthouse functioning gate',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.AdmBase,0);")
    m.command('repair Lighthouse',"TQA.Pillage('A','BUILDING_LIGHTHOUSE',false)")
    m.command('prepare Sacristan Temple',"TQA.Add('SA','BUILDING_SHRINE');TQA.Add('SA','BUILDING_TEMPLE');")
    m.command('capture Prophet and Faith baseline',"TQA.ProphetBase=TQA.GPP('GREAT_PERSON_CLASS_PROPHET');TQA.FaithBase=TQA.Raw('A','YIELD_FAITH');",'PlotInfo')
    m.command('unlock Divine Right',"TQA.Civic('CIVIC_DIVINE_RIGHT',true)")
    m.check('Sacristan established',f'TQA.Service("A","{S3}",true)')
    m.check('Sacristan Prophet point',"TQA.Equal('Prophet delta',TQA.GPP('GREAT_PERSON_CLASS_PROPHET')-TQA.ProphetBase,1);")
    m.check('Sacristan ten percent Faith',"TQA.Equal('Faith multiplier',TQA.Raw('A','YIELD_FAITH')/TQA.FaithBase,1.1,.02);")
    m.command('pillage Sacristan supply',"TQA.Resource('MA1','RESOURCE_COTTON',nil)")
    m.check('Sacristan persists without supply',f'TQA.Service("A","{S3}",true)')
    m.check('Sacristan Prophet supply gate',"TQA.Equal('Prophet inactive',TQA.GPP('GREAT_PERSON_CLASS_PROPHET')-TQA.ProphetBase,0);")
    m.command('restore Sacristan supply',"TQA.Resource('MA1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION')")
    m.command('prepare Fashion House supplied venues',"TQA.Resource('MD1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION');TQA.Resource('MD2','RESOURCE_DYES','IMPROVEMENT_PLANTATION');")
    m.command('capture performance venue baseline',"TQA.ArtistBase=TQA.GPP('GREAT_PERSON_CLASS_ARTIST');TQA.TourBase={};for _,site in ipairs({'TE','WE1','WE2','WE3'}) do TQA.TourBase[site]=TQA.Tour(site);end",'PlotInfo')
    m.command('unlock Opera and Ballet',"TQA.Civic('CIVIC_OPERA_BALLET',true)")
    for site in ('TE','WE1','WE2','WE3'):
        m.check('performance Service Tourism '+site,f'TQA.Equal("Tourism {site}",TQA.Tour("{site}")-TQA.TourBase["{site}"],2);')
    m.check('four performance Services give four Artist points',"TQA.Equal('Artist delta',TQA.GPP('GREAT_PERSON_CLASS_ARTIST')-TQA.ArtistBase,4);")
    m.check('Theater Stage Manager present',f'TQA.Service("E","{S4}",true)')
    for i,branch in enumerate(('BOLSHOI','BROADWAY','SYDNEY'),1):
        m.check('Wonder exact host '+branch,f'''local c=TQA.C('E');local b=GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_{branch}; assert(c:GetBuildings():HasBuilding(b.Index),'missing Wonder Service');TQA.Equal('host location',c:GetBuildings():GetBuildingLocation(b.Index),TQA.Site('WE{i}'):GetIndex());''','CSC_AdjacencyGameplay')
    m.command('remove Specialty supply only',"TQA.Resource('MD2','RESOURCE_DYES',nil)")
    for site in ('TE','WE1','WE2','WE3'):
        m.check('lost Specialty deactivates Tourism '+site,f'TQA.Equal("lost supply {site}",TQA.Tour("{site}")-TQA.TourBase["{site}"],0);')
    m.check('lost Specialty deactivates Artist points',"TQA.Equal('Artist inactive',TQA.GPP('GREAT_PERSON_CLASS_ARTIST')-TQA.ArtistBase,0);")
    m.command('restore Specialty supply',"TQA.Resource('MD2','RESOURCE_DYES','IMPROVEMENT_PLANTATION')")
    m.check('restored Specialty restores all Artist points',"TQA.Equal('Artist restored',TQA.GPP('GREAT_PERSON_CLASS_ARTIST')-TQA.ArtistBase,4);")


def local_recheck(m):
    m.by('settled two local stages Production','A',W,'PRODUCTION',3)
    m.by('settled two local stages Gold','A',W,'GOLD',3)
    m.by('settled Lighthouse customer Production','A','BUILDING_LIGHTHOUSE','PRODUCTION',1)
    m.command('make Harbor terrain coastal',"TerrainBuilder.SetTerrainType(TQA.Site('HA'),GameInfo.Terrains.TERRAIN_COAST.Index)")
    m.by('coastal Lighthouse return Production','A',W,'PRODUCTION',3)
    m.by('coastal Lighthouse customer Production','A','BUILDING_LIGHTHOUSE','PRODUCTION',1)


def trade(m):
    m.command('prepare normal domestic trade', '''TQA.Civic('CIVIC_FOREIGN_TRADE',true);TQA.Civic('CIVIC_GUILDS',true);TQA.Civic('CIVIC_HUMANISM',true);
local ring=Map.GetAdjacentPlots(17,8);TQA.ResourceSite('MB1','B',ring[4]);TQA.ResourceSite('MB2','B',ring[5]);
TQA.Resource('MB1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION');TQA.Resource('MB2','RESOURCE_DYES','IMPROVEMENT_PLANTATION');
TQA.Add('QB','BUILDING_CSC_TAILORS_FASHION_HOUSE');local c=TQA.C('C');local unit=UnitManager.InitUnit(0,GameInfo.Units.UNIT_TRADER.Index,c:GetX(),c:GetY());
assert(unit,'Trader creation failed');local f=Game:GetProperty('CSC_TAILORS_QA');f.Trader=unit:GetID();TQA.Store(f);''')
    m.command('capture pre-route native yields', '''TQA.TradeBase={};for _,city in ipairs({'B','C'}) do for _,y in ipairs({'CULTURE','PRODUCTION','GOLD'}) do TQA.TradeBase[city..y]=TQA.Raw(city,'YIELD_'..y);end;end;TQA.TradeBase.Amenity=TQA.C('C'):GetGrowth():GetAmenities();''','PlotInfo')
    m.command('start actual domestic route', '''local f=Game:GetProperty('CSC_TAILORS_QA');local unit=Players[0]:GetUnits():FindID(f.Trader);local target=TQA.C('B');local params={};
params[UnitOperationTypes.PARAM_X0]=target:GetX();params[UnitOperationTypes.PARAM_Y0]=target:GetY();
params[UnitOperationTypes.PARAM_X1]=unit:GetX();params[UnitOperationTypes.PARAM_Y1]=unit:GetY();
print('TRADE_CAPACITY',Players[0]:GetTrade():GetOutgoingRouteCapacity());
assert(UnitManager.CanStartOperation(unit,UnitOperationTypes.MAKE_TRADE_ROUTE,nil,params),'native route unavailable');
UnitManager.RequestOperation(unit,UnitOperationTypes.MAKE_TRADE_ROUTE,params);''','PlotInfo')
    m.check('route exists in native origin list',"local routes=TQA.C('C'):GetTrade():GetOutgoingRoutes();print('ROUTE_COUNT',#routes);assert(#routes==1);")
    m.check('both stages each mark route once', '''local c=TQA.C('C');TQA.Equal('Tailor route',c:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE') or 0,1);TQA.Equal('Fashion route',c:GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE') or 0,1);''')
    m.check('two export return channels delivered', '''TQA.Equal('Tailor export',TQA.BY('B','BUILDING_CSC_TAILORS_TAILOR','YIELD_PRODUCTION'),1);TQA.Equal('Fashion export with four-site free baseline',TQA.BY('B','BUILDING_CSC_TAILORS_FASHION_HOUSE','YIELD_PRODUCTION'),1);''')
    m.check('two route Culture transactions',"TQA.Equal('origin Culture',TQA.Raw('C','YIELD_CULTURE')-TQA.TradeBase.CCULTURE,2,.03);")
    m.check('two route Amenity transactions',"TQA.Equal('origin Amenities',TQA.C('C'):GetGrowth():GetAmenities()-TQA.TradeBase.Amenity,2);")
    m.command('end route by removing Trader',"local f=Game:GetProperty('CSC_TAILORS_QA');UnitManager.Kill(Players[0]:GetUnits():FindID(f.Trader));")
    m.check('ended route clears both import flags', '''TQA.Equal('Tailor cleared',TQA.C('C'):GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE') or 0,0);TQA.Equal('Fashion cleared',TQA.C('C'):GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE') or 0,0);''')


def multiseller(m):
    m.command('prepare second Fashion House supplier', '''TQA.Pop('E',9);TQA.District('QF','F','DISTRICT_CSC_TAILORS_QUARTER',12,18);
local count=0;for _,p in ipairs(Map.GetAdjacentPlots(12,18)) do if p:GetDistrictType()==-1 then count=count+1;TQA.ResourceSite('MFAB'..count,'F',p);if count==2 then break;end;end;end;assert(count==2);
TQA.Resource('MFAB1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION');TQA.Resource('MFAB2','RESOURCE_DYES','IMPROVEMENT_PLANTATION');TQA.Add('QF','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP');''')
    m.command('capture before second seller',"TQA.ArtistMultiBase=TQA.GPP('GREAT_PERSON_CLASS_ARTIST');TQA.MultiTour={};for _,s in ipairs({'TE','WE1','WE2','WE3'}) do TQA.MultiTour[s]=TQA.Tour(s);end",'PlotInfo')
    m.command('activate second supplier',f'TQA.Add("QF","{F}")')
    m.check('second supplier per-site Tourism stacking', '''local p=TQA.Site('QF');for _,s in ipairs({'TE','WE1','WE2','WE3'}) do local v=TQA.Site(s);local adjacent=Map.GetPlotDistance(p:GetX(),p:GetY(),v:GetX(),v:GetY())==1;TQA.Equal('second seller '..s,TQA.Tour(s)-TQA.MultiTour[s],adjacent and 2 or 0);end''')
    m.by('original supplier keeps independently rounded sites','D',F,'PRODUCTION',4)
    m.check('second supplier Artist points stack per venue', '''local p=TQA.Site('QF');local n=0;for _,s in ipairs({'TE','WE1','WE2','WE3'}) do local v=TQA.Site(s);if Map.GetPlotDistance(p:GetX(),p:GetY(),v:GetX(),v:GetY())==1 then n=n+1;end;end;TQA.Equal('second seller Artist points',TQA.GPP('GREAT_PERSON_CLASS_ARTIST')-TQA.ArtistMultiBase,n);TQA.Equal('second seller returns',TQA.BY('F','BUILDING_CSC_TAILORS_FASHION_HOUSE','YIELD_PRODUCTION'),n);''')
    m.command('remove one supplier Specialty',"TQA.Resource('MFAB2','RESOURCE_DYES',nil)")
    m.check('one supplier loss preserves other supplier Tourism', '''for _,s in ipairs({'TE','WE1','WE2','WE3'}) do TQA.Equal('remaining supplier '..s,TQA.Tour(s),TQA.MultiTour[s]);end''')
    m.check('ordinary sales persist without service supply', '''local p=TQA.Site('QF');local n=0;for _,s in ipairs({'TE','WE1','WE2','WE3'}) do local v=TQA.Site(s);if Map.GetPlotDistance(p:GetX(),p:GetY(),v:GetX(),v:GetY())==1 then n=n+1;end;end;TQA.Equal('unsupplied population returns',TQA.BY('F','BUILDING_CSC_TAILORS_FASHION_HOUSE','YIELD_PRODUCTION'),n);''')
    m.command('second supplier restored',"TQA.Resource('MFAB2','RESOURCE_DYES','IMPROVEMENT_PLANTATION')")


def regional(m):
    m.command('isolate regional Fashion House',f'''TQA.Remove('A','{F}');TQA.Remove('B','{F}');TQA.Remove('F','{F}');TQA.Remove('D','{F}');
TQA.City('R6',10,11,5);TQA.City('R7',3,17,5);''')
    m.command('capture regional Amenities baseline',"TQA.RegionalBase={};for _,c in ipairs({'D','E','R6','R7'}) do TQA.RegionalBase[c]=TQA.C(c):GetGrowth():GetAmenities();end",'PlotInfo')
    m.command('restore only regional source',f'TQA.Add("QD","{F}")')
    for c,distance,delta in [('D',2,1),('E',5,1),('R6',6,1),('R7',7,0)]:
        m.check(f'regional Amenities at radius {distance}',f'''local c=TQA.C('{c}');local q=TQA.Site('QD');TQA.Equal('distance',Map.GetPlotDistance(c:GetX(),c:GetY(),q:GetX(),q:GetY()),{distance});TQA.Equal('regional Amenity',c:GetGrowth():GetAmenities()-TQA.RegionalBase['{c}'],{delta});''')


def static_native(m):
    m.check('Tailors native definitions', '''local d=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER;assert(d.PrereqCivic=='CIVIC_CRAFTSMANSHIP' and d.Cost==60 and d.Maintenance==1);
for _,entry in ipairs({{'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',80,2,0},{'BUILDING_CSC_TAILORS_TAILOR',160,2,1},{'BUILDING_CSC_TAILORS_FASHION_HOUSE',250,3,1}}) do local b=GameInfo.Buildings[entry[1]];assert(b.Cost==entry[2] and b.Maintenance==entry[3] and b.CitizenSlots==entry[4],entry[1]);end;
assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP.PrereqTech=='TECH_CONSTRUCTION');assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR.PrereqCivic=='CIVIC_GUILDS');assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_FASHION_HOUSE.PrereqCivic=='CIVIC_HUMANISM');
assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI.CitizenSlots==0);assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.CitizenSlots==0);assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY.CitizenSlots==0);''')


def recovered(m):
    m.check('reload retains native local exchanges',f'''TQA.Equal('Workshop Production',TQA.BY('A','{W}','YIELD_PRODUCTION'),3);TQA.Equal('Workshop Gold',TQA.BY('A','{W}','YIELD_GOLD'),3);TQA.Equal('Lighthouse Production',TQA.BY('A','BUILDING_LIGHTHOUSE','YIELD_PRODUCTION'),1);''')
    m.check('reload retains all three Wonder service locations', '''for i,branch in ipairs({'BOLSHOI','BROADWAY','SYDNEY'}) do local c=TQA.C('E');local b=GameInfo.Buildings['BUILDING_CSC_TAILORS_STAGE_4_SERVICE_'..branch];assert(c:GetBuildings():HasBuilding(b.Index));TQA.Equal('Wonder location '..branch,c:GetBuildings():GetBuildingLocation(b.Index),TQA.Site('WE'..i):GetIndex());end''','CSC_AdjacencyGameplay')
    m.command('recovered performance baseline without Specialty',"TQA.Resource('MD2','RESOURCE_DYES',nil)")
    m.command('capture recovered Service counters',"TQA.RecoveryBase={Artist=TQA.GPP('GREAT_PERSON_CLASS_ARTIST'),Tour={}};for _,s in ipairs({'TE','WE1','WE2','WE3'}) do TQA.RecoveryBase.Tour[s]=TQA.Tour(s);end",'PlotInfo')
    m.command('recovered performance supply restored',"TQA.Resource('MD2','RESOURCE_DYES','IMPROVEMENT_PLANTATION')")
    m.check('recovered four Service Artist points',"TQA.Equal('Artist delta',TQA.GPP('GREAT_PERSON_CLASS_ARTIST')-TQA.RecoveryBase.Artist,4);")
    for site in ('TE','WE1','WE2','WE3'):m.check('recovered Tourism '+site,f'TQA.Equal("Tourism {site}",TQA.Tour("{site}")-TQA.RecoveryBase.Tour["{site}"],2);')
    m.command('recovered conventional supply baseline',"TQA.Resource('MA1','RESOURCE_COTTON',nil);TQA.Resource('MA2','RESOURCE_CSC_FLAX',nil)")
    m.command('capture conventional counters',"TQA.ConventionalBase={Admiral=TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL'),Prophet=TQA.GPP('GREAT_PERSON_CLASS_PROPHET'),Faith=TQA.Raw('A','YIELD_FAITH')};",'PlotInfo')
    m.command('restore conventional Base supply',"TQA.Resource('MA1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION')")
    m.check('recovered Dockmaster Admiral point',"TQA.Equal('Admiral',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.ConventionalBase.Admiral,1);")
    m.check('recovered Sacristan Prophet point',"TQA.Equal('Prophet',TQA.GPP('GREAT_PERSON_CLASS_PROPHET')-TQA.ConventionalBase.Prophet,1);")
    m.check('recovered Sacristan Faith',"TQA.Equal('Faith',TQA.Raw('A','YIELD_FAITH')/TQA.ConventionalBase.Faith,1.1,.02);")
    # Lighthouse, Shrine and Temple each already contribute a native slot.
    # TE is deliberately outside E's workable radius; use legal_specialists.
    for city,site,expected in [('A','QA',2),('A','HA',2),('A','SA',3),('E','WE1',0),('E','WE2',0),('E','WE3',0)]:
        m.check('usable Citizen slots '+site,f'local max,current=TQA.Slots("{city}","{site}");TQA.Equal("slots {site}",max,{expected});')


def native_purchase(m):
    m.command('prepare normal Tailor purchase',f'''TQA.Remove('B','{T}');TQA.Pop('C',11);TQA.Pop('C',10);TQA.Pop('F',7);TQA.Pop('F',6);TQA.Civic('CIVIC_GUILDS',true);''')
    m.command('capture normal purchase baseline',"TQA.PurchaseBase={CC=TQA.Raw('C','YIELD_CULTURE'),FC=TQA.Raw('F','YIELD_CULTURE'),BP=TQA.Raw('B','YIELD_PRODUCTION'),BG=TQA.Raw('B','YIELD_GOLD')};",'PlotInfo')
    m.command('purchase Tailor normally',f'''local c=TQA.C('B');local p={{}};p[CityCommandTypes.PARAM_BUILDING_TYPE]=GameInfo.Buildings.{T}.Hash;p[CityCommandTypes.PARAM_YIELD_TYPE]=GameInfo.Yields.YIELD_GOLD.Index;local can=CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,false,p,true);print('CAN_PURCHASE_TAILOR',can);assert(can,'Tailor not purchasable');CityManager.RequestCommand(c,CityCommandTypes.PURCHASE,p);''','PlotInfo')
    m.check('purchased Tailor immediately supplies both customer families',"TQA.Equal('C Culture',TQA.Raw('C','YIELD_CULTURE')-TQA.PurchaseBase.CC,2,.06);TQA.Equal('F Culture',TQA.Raw('F','YIELD_CULTURE')-TQA.PurchaseBase.FC,.6,.04);")
    m.check('purchased Tailor receives customer returns plus local exchange',"TQA.Equal('B Production',TQA.Raw('B','YIELD_PRODUCTION')-TQA.PurchaseBase.BP,3.6,.08);TQA.Equal('B Gold',TQA.Raw('B','YIELD_GOLD')-TQA.PurchaseBase.BG,3.6,.08);")
    m.command('native purchase followed by population update',"TQA.Pop('C',11);TQA.Pop('C',10);TQA.Pop('F',7);TQA.Pop('F',6)")
    m.check('population refresh preserves intended customer Culture',"TQA.Equal('C Culture after population',TQA.Raw('C','YIELD_CULTURE')-TQA.PurchaseBase.CC,2,.06);TQA.Equal('F Culture after population',TQA.Raw('F','YIELD_CULTURE')-TQA.PurchaseBase.FC,.6,.04);")


def closing_probes(m):
    m.command('diagnose serialized notification cache', '''local known={};for row in GameInfo.CSC_AbilityAttachModifiers() do if row.AbilityEffectModifierId then known[DB.MakeHash(row.AbilityEffectModifierId)]=row.AbilityEffectModifierId;end;end;
local cache=ReadCustomData('CSC_AbilitiesCaching_Player'..tostring(Game.GetLocalPlayer()));
for city,entries in pairs(cache or {}) do for key,value in pairs(entries) do print('CACHE_ENTRY',city,type(key),key,known[key],value.StackAmount,value[DB.MakeHash('StackAmount')]);end;end;
local ok,err=pcall(OnRefreshCityQuarters);print('NOTIFICATION_REFRESH',ok,err);''','CSC_UI_Notifications')
    m.command('create workable Theater service',f'''TQA.Add('QA','{F}');TQA.Add('TA','BUILDING_AMPHITHEATER');''')
    for site,expected in [('QA',2),('HA',2),('SA',3),('TA',2)]:
        m.check('native workable Citizen slots '+site,f'''local p=TQA.Site('{site}');local c=TQA.C('A');assert(Map.GetPlotDistance(c:GetX(),c:GetY(),p:GetX(),p:GetY())<=3);local max=TQA.Slots('A','{site}');TQA.Equal('total slots {site}',max,{expected});''')
    m.command('capture vanilla point counter baseline',"TQA.PointProbe=TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL');print('BEFORE_LIGHTHOUSE',TQA.PointProbe);",'PlotInfo')
    m.command('remove vanilla Lighthouse for counter control',"TQA.Remove('A','BUILDING_LIGHTHOUSE')")
    m.command('observe vanilla point counter update',"print('AFTER_LIGHTHOUSE',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL'),'DELTA',TQA.GPP('GREAT_PERSON_CLASS_ADMIRAL')-TQA.PointProbe);",'PlotInfo')
    m.command('restore vanilla Lighthouse',"TQA.Add('HA','BUILDING_LIGHTHOUSE')")
    m.command('inspect regional source location',f'''local c=TQA.C('D');local plot=Map.GetPlotByIndex(c:GetBuildings():GetBuildingLocation(GameInfo.Buildings.{F}.Index));print('FASHION_LOCATION',plot:GetX(),plot:GetY());for _,name in ipairs({{'D','E','R6','R7'}}) do local v=TQA.C(name);print('REGIONAL_DISTANCES',name,Map.GetPlotDistance(v:GetX(),v:GetY(),plot:GetX(),plot:GetY()),Map.GetPlotDistance(v:GetX(),v:GetY(),c:GetX(),c:GetY()));end;''')
    m.command('remove source before normal Fashion purchase',f"TQA.Remove('D','{F}');TQA.Remove('A','{F}');")
    m.command('capture regional baseline before purchase',"TQA.RegionPurchase={};for _,name in ipairs({'D','E','R6','R7'}) do TQA.RegionPurchase[name]=TQA.C(name):GetGrowth():GetAmenities();end",'PlotInfo')
    m.command('purchase Fashion House normally',f'''local c=TQA.C('D');local p={{}};p[CityCommandTypes.PARAM_BUILDING_TYPE]=GameInfo.Buildings.{F}.Hash;p[CityCommandTypes.PARAM_YIELD_TYPE]=GameInfo.Yields.YIELD_GOLD.Index;assert(CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,false,p,true));CityManager.RequestCommand(c,CityCommandTypes.PURCHASE,p);''','PlotInfo')
    m.command('observe purchased regional Amenities',"for _,name in ipairs({'D','E','R6','R7'}) do local g=TQA.C(name):GetGrowth();print('PURCHASED_REGIONAL',name,g:GetAmenities()-TQA.RegionPurchase[name],g:GetAmenitiesFromDistricts(),g:GetAmenitiesFromEntertainment());end",'PlotInfo')
    for improvement,expected in [('IMPROVEMENT_PLANTATION',1),('IMPROVEMENT_INDUSTRY',2),('IMPROVEMENT_CORPORATION',3)]:
        m.command('material producer baseline '+improvement,f"TQA.Remove('A','{W}');TQA.Resource('MA1','RESOURCE_COTTON','{improvement}');")
        m.command('capture material plot baseline '+improvement,"TQA.MaterialPlot={P=TQA.PY('MA1','YIELD_PRODUCTION'),G=TQA.PY('MA1','YIELD_GOLD')};",'PlotInfo')
        m.command('restore Workshop for producer '+improvement,f"TQA.Add('QA','{W}')")
        m.check('material producer native exchange '+improvement,f"TQA.Equal('material Production',TQA.PY('MA1','YIELD_PRODUCTION')-TQA.MaterialPlot.P,{expected});TQA.Equal('material Gold',TQA.PY('MA1','YIELD_GOLD')-TQA.MaterialPlot.G,{expected});")
    m.command('restore ordinary material after producer tests',"TQA.Resource('MA1','RESOURCE_COTTON','IMPROVEMENT_PLANTATION')")


def ownership_purchase(m):
    m.command('prepare real material purchase',"TQA.Resource('MA1','RESOURCE_COTTON',nil);TQA.Resource('MA2','RESOURCE_CSC_FLAX',nil);TQA.Resource('MA3','RESOURCE_DYES',nil);local p=TQA.Site('MA3');WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),-1,-1);CSC_RefreshAdjacencies();")
    district="local ds=TQA.C('A'):GetDistricts();local q=nil;for i=0,ds:GetNumDistricts()-1 do local d=ds:GetDistrictByIndex(i);if d:GetType()==GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index then q=d;break;end;end;assert(q);"
    m.command('capture native purchase baseline',district+"Game:SetProperty('CSC_QA_OWN_BASE',q:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index));")
    m.command('purchase material normally',"local p=TQA.Site('MA3');local a={};a[CityCommandTypes.PARAM_PLOT_PURCHASE]=true;a[CityCommandTypes.PARAM_X]=p:GetX();a[CityCommandTypes.PARAM_Y]=p:GetY();assert(CityManager.CanStartCommand(TQA.C('A'),CityCommandTypes.PURCHASE,a));CityManager.RequestCommand(TQA.C('A'),CityCommandTypes.PURCHASE,a);",'PlotInfo')
    m.check('purchased material immediately updates native yield',district+"assert(TQA.Site('MA3'):GetOwner()==0);TQA.Equal('ownership delta',q:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index)-Game:GetProperty('CSC_QA_OWN_BASE'),1);",'CSC_AdjacencyGameplay')


def producer_returns(m):
    for city,site,building,resource,source in [('A','MA1',W,'RESOURCE_COTTON','QA'),('D','MD2',F,'RESOURCE_DYES','QD')]:
        for tier,expected in [('IMPROVEMENT_PLANTATION',1),('IMPROVEMENT_INDUSTRY',2),('IMPROVEMENT_CORPORATION',3)]:
            label=city+' '+tier
            m.command('prepare producer baseline '+label,f"TQA.Resource('{site}','{resource}','{tier}');TQA.Remove('{city}','{building}');")
            m.command('capture producer baseline '+label,f"TQA.ProducerBase={{P=TQA.PY('{site}','YIELD_PRODUCTION'),G=TQA.PY('{site}','YIELD_GOLD')}};",'PlotInfo')
            m.command('restore producer source '+label,f"TQA.Add('{source}','{building}')")
            m.check('material producer total '+label,f"TQA.Equal('Production',TQA.PY('{site}','YIELD_PRODUCTION')-TQA.ProducerBase.P,{expected});TQA.Equal('Gold',TQA.PY('{site}','YIELD_GOLD')-TQA.ProducerBase.G,{expected});")


def customer_purchase_regression(m):
    m.command('prepare existing customer buildings',f"TQA.Add('QB','{W}');TQA.Add('MC','BUILDING_MARKET');TQA.Add('SC','BUILDING_SHRINE');TQA.Add('SC','BUILDING_TEMPLE');TQA.Add('MF','BUILDING_MARKET');")
    native_purchase(m)
    m.command('remove supplier without population change',f"TQA.Remove('B','{T}')")
    m.check('removed supplier immediately clears customer Culture',"TQA.Equal('C cleared',TQA.Raw('C','YIELD_CULTURE')-TQA.PurchaseBase.CC,0,.06);TQA.Equal('F cleared',TQA.Raw('F','YIELD_CULTURE')-TQA.PurchaseBase.FC,0,.04);")


def purchase_building(m, city, building, label):
    m.command(label,f"local c=TQA.C('{city}');local p={{}};p[CityCommandTypes.PARAM_BUILDING_TYPE]=GameInfo.Buildings.{building}.Hash;p[CityCommandTypes.PARAM_YIELD_TYPE]=GameInfo.Yields.YIELD_GOLD.Index;assert(CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,false,p,true),'Native building purchase unavailable');CityManager.RequestCommand(c,CityCommandTypes.PURCHASE,p);",'PlotInfo')


def capital_material_returns(m):
    for building,site,resource in [(W,'MP1','RESOURCE_COTTON'),(F,'MP2','RESOURCE_DYES')]:
        for tier,expected in [('IMPROVEMENT_PLANTATION',1),('IMPROVEMENT_INDUSTRY',2),('IMPROVEMENT_CORPORATION',3)]:
            label=building+' '+tier
            m.command('prepare capital material '+label,f"TQA.Resource('{site}','{resource}','{tier}');if TQA.Has('A','{building}') then TQA.Remove('A','{building}');end;")
            m.command('capture capital material baseline '+label,f"TQA.CapitalBase={{P=TQA.PY('{site}','YIELD_PRODUCTION'),G=TQA.PY('{site}','YIELD_GOLD')}};print('BASELINE',TQA.CapitalBase.P,TQA.CapitalBase.G);",'PlotInfo')
            purchase_building(m,'A',building,'purchase capital source '+label)
            m.check('capital material return '+label,f"TQA.Equal('Production',TQA.PY('{site}','YIELD_PRODUCTION')-TQA.CapitalBase.P,{expected});TQA.Equal('Gold',TQA.PY('{site}','YIELD_GOLD')-TQA.CapitalBase.G,{expected});")


def producer_returns_native(m):
    m.command('unlock native Fashion House purchases',f"TQA.Civic('CIVIC_HUMANISM',true);TQA.Add('QD','{W}');")
    for city,site,building,resource in [('A','MA1',W,'RESOURCE_COTTON'),('D','MD2',F,'RESOURCE_DYES')]:
        for tier,expected in [('IMPROVEMENT_PLANTATION',1),('IMPROVEMENT_INDUSTRY',2),('IMPROVEMENT_CORPORATION',3)]:
            label=city+' '+tier
            m.command('prepare native producer baseline '+label,f"TQA.Resource('{site}','{resource}','{tier}');TQA.Remove('{city}','{building}');")
            m.command('capture native producer baseline '+label,f"TQA.NativeProducerBase={{P=TQA.PY('{site}','YIELD_PRODUCTION'),G=TQA.PY('{site}','YIELD_GOLD')}};",'PlotInfo')
            purchase_building(m,city,building,'purchase producer source '+label)
            m.check('native purchased material producer total '+label,f"TQA.Equal('Production',TQA.PY('{site}','YIELD_PRODUCTION')-TQA.NativeProducerBase.P,{expected});TQA.Equal('Gold',TQA.PY('{site}','YIELD_GOLD')-TQA.NativeProducerBase.G,{expected});")


def bakers_producer_returns(m):
    m.command('create Bakers control district', "TQA.City('G',29,17,10);TQA.District('QG','G','DISTRICT_CSC_BAKERS_QUARTER',31,17);local ring=Map.GetAdjacentPlots(31,17);TQA.ResourceSite('MG1','G',ring[1]);TQA.ResourceSite('MG2','G',ring[2]);")
    for building,site,resource,tiers in [
        ('BUILDING_CSC_BAKERS_WATER_MILL','MG1','RESOURCE_WHEAT',[('IMPROVEMENT_FARM',1)]),
        ('BUILDING_CSC_BAKERS_WIND_MILL','MG1','RESOURCE_WHEAT',[('IMPROVEMENT_FARM',1)]),
        ('BUILDING_CSC_BAKERS_CAFE','MG2','RESOURCE_COFFEE',[('IMPROVEMENT_PLANTATION',1),('IMPROVEMENT_INDUSTRY',2),('IMPROVEMENT_CORPORATION',3)]),
    ]:
        for tier,expected in tiers:
            label=building+' '+tier
            m.command('prepare Bakers control '+label,f"TQA.Resource('{site}','{resource}','{tier}');TQA.Remove('G','{building}');")
            m.command('capture Bakers producer baseline '+label,f"TQA.BakersBase={{P=TQA.PY('{site}','YIELD_PRODUCTION'),G=TQA.PY('{site}','YIELD_GOLD')}};",'PlotInfo')
            m.command('activate Bakers control '+label,f"TQA.Add('QG','{building}')")
            m.check('Bakers native total '+label,f"TQA.Equal('Production',TQA.PY('{site}','YIELD_PRODUCTION')-TQA.BakersBase.P,{expected});TQA.Equal('Gold',TQA.PY('{site}','YIELD_GOLD')-TQA.BakersBase.G,{expected});")
        m.command('remove Bakers control source '+building,f"TQA.Remove('G','{building}')")


def producer_stacking(m):
    m.command('create second Fashion source adjacent to material', "local target=TQA.Site('MD2');local chosen=nil;for _,p in ipairs(Map.GetAdjacentPlots(target:GetX(),target:GetY())) do if p:GetDistrictType()==-1 and p:GetResourceType()==-1 then chosen=p;break;end;end;assert(chosen);TQA.District('QS','E','DISTRICT_CSC_TAILORS_QUARTER',chosen:GetX(),chosen:GetY());")
    for tier,expected in [('IMPROVEMENT_PLANTATION',2),('IMPROVEMENT_INDUSTRY',4),('IMPROVEMENT_CORPORATION',6)]:
        m.command('prepare two-source baseline '+tier,f"TQA.Remove('D','{F}');TQA.Remove('E','{F}');TQA.Resource('MD2','RESOURCE_DYES','{tier}');")
        m.command('capture two-source baseline '+tier,"TQA.StackBase={P=TQA.PY('MD2','YIELD_PRODUCTION'),G=TQA.PY('MD2','YIELD_GOLD')};",'PlotInfo')
        m.command('activate two Fashion sources '+tier,f"TQA.Add('QD','{F}');TQA.Add('QS','{F}');")
        m.check('two independent Fashion sources stack '+tier,f"TQA.Equal('two-source Production',TQA.PY('MD2','YIELD_PRODUCTION')-TQA.StackBase.P,{expected});TQA.Equal('two-source Gold',TQA.PY('MD2','YIELD_GOLD')-TQA.StackBase.G,{expected});")
    m.command('remove extra source after stacking',f"TQA.Remove('E','{F}')")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--groups',nargs='+',default=['material_local','stage3','stage4'])
    a=p.parse_args()
    states=tuner.states();tuner.states=lambda:states
    m=Matrix(a.output)
    source=(ROOT/'project/tests/qa/placement.lua').read_text()+'\n'+(ROOT/'project/tests/qa/tailors_world.lua').read_text()
    m.command('load gameplay QA helpers',source)
    m.command('load UI QA helpers',source,'PlotInfo')
    for group in a.groups:
        try:globals()[group](m)
        except Exception as exc:
            (a.output/(group+'-blocked.txt')).write_text(str(exc));print('BLOCKED group '+group+': '+str(exc),flush=True)
    print('Matrix complete; see matrix.json',flush=True)


if __name__=='__main__':main()
