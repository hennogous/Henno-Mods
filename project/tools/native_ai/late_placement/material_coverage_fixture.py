"""Shared-controller callback for a separate, disposable payout qualification.

It grants declared human-0 fixtures and reads actual UI building yields. Never
call it from the ordinary full-game observer. The owning NativeSession supplies
the controller and performs process/preference/package cleanup afterwards.
"""
from pathlib import Path
import time

from driver import lua,parse,read,require,write_json

HERE=Path(__file__).resolve().parent
FIELDS=('windFood','cafeFood','workshopCulture')
DELTAS={'none':(0,0,0),'farm':(1,0,0),'maple':(0,1,0),
        'bamboo':(0,0,1),'unmapped':(0,0,0)}


def differences(before,after):
    return tuple(after[k]-before[k]for k in FIELDS)


def qualify_rows(baseline,measurements):
    require(set(measurements)==set(DELTAS),'Incomplete material payout phases')
    for phase,expected in DELTAS.items():
        row=measurements[phase]
        require(row['turn']==baseline['turn'],'Payout fixture clock changed')
        require(all(abs(actual-wanted)<1e-6 for actual,wanted in zip(differences(baseline,row),expected)),
                'Unexpected material payout: '+phase)
    return dict(verified=True,baseline=baseline,measurements=measurements,
                deltas={k:list(differences(baseline,v))for k,v in measurements.items()},
                diagnostic_only=True,fixture_grants=True,ai_outcome=False,
                final_none='Test improvements removed; Quarter/building/resource grants remain until disposable session closes')


def run(controller,output,config):
    require(config.get('diagnosticOnly')is True and config.get('player')==0,
            'Explicit disposable human fixture required')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    write_json(output/'config.json',config)
    code=read(HERE/'material_coverage_fixture.lua')
    (output/'material_coverage_fixture.lua').write_text(code,encoding='utf-8')
    controller.cmd(code,'CSC_AdjacencyGameplay','define-material-payout-fixture')
    raw=controller.cmd('CSC_MaterialCoverageFixture.Setup('+lua(config)+')',
                       'CSC_AdjacencyGameplay','prepare-material-payout-fixture')
    (output/'setup.txt').write_text(raw,encoding='utf-8')
    require('CSC_MATERIAL_COVERAGE_SETUP'in raw,'Fixture preparation incomplete')

    def capture(phase,attempt):
        # UI owns GetBuildingYield; Gameplay separately records physical plots
        # and exact producer locations. Neither read invokes an AI valuation.
        code='local c='+lua(config)+'''
local city=assert(Players[0]:GetCities():FindID(c.city))
local function amount(name,yield)
 local id=assert(GameInfo.Buildings[name]).Index
 assert(city:GetBuildings():HasBuilding(id))
 return assert(city:GetBuildingYield(id,yield))
end
print('CSC_MATERIAL_COVERAGE_YIELDS='..string.format(
 '{"turn":%d,"windFood":%.8g,"cafeFood":%.8g,"workshopCulture":%.8g}',
 Game.GetCurrentGameTurn(),amount('BUILDING_CSC_BAKERS_WIND_MILL','YIELD_FOOD'),
 amount('BUILDING_CSC_BAKERS_CAFE','YIELD_FOOD'),
 amount('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','YIELD_CULTURE')))
'''
        raw=controller.cmd(code,'PlotInfo','material-payout-'+phase+'-'+str(attempt))
        (output/(phase+'-'+str(attempt)+'.txt')).write_text(raw,encoding='utf-8')
        row=parse(raw,'CSC_MATERIAL_COVERAGE_YIELDS')
        require(row['turn']==config['turn'],'Fixture observation crossed a turn')
        return row

    baseline=None;measurements={}
    for step,phase in enumerate(('none','farm','maple','bamboo','unmapped','none')):
        label=str(step)+'-'+phase
        raw=controller.cmd('CSC_MaterialCoverageFixture.Activate('+lua(phase)+')',
                           'CSC_AdjacencyGameplay','activate-material-payout-'+label)
        (output/('activate-'+label+'.txt')).write_text(raw,encoding='utf-8')
        require('CSC_MATERIAL_COVERAGE_WORLD'in raw,'Physical supplier readback missing')
        # Separate commands let native modifier/UI updates settle. Retry reads,
        # never the world mutation. A timeout preserves all discrepant samples.
        deadline=time.monotonic()+60;last=None;stable=0;attempt=0
        while True:
            row=capture(label,attempt);attempt+=1
            correct=baseline is None or all(abs(a-b)<1e-6 for a,b in zip(differences(baseline,row),DELTAS[phase]))
            stable=stable+1 if correct and row==last else 0
            if stable>=1:break
            require(time.monotonic()<deadline,'Native payout did not settle: '+phase)
            last=row;time.sleep(.25)
        if baseline is None:baseline=row
        measurements[phase]=row
        raw=controller.cmd('CSC_MaterialCoverageFixture.Observe()',
                           'CSC_AdjacencyGameplay','settled-material-world-'+label)
        (output/('settled-world-'+label+'.txt')).write_text(raw,encoding='utf-8')
        require('CSC_MATERIAL_COVERAGE_WORLD'in raw,'Settled physical supplier readback missing')
    result=qualify_rows(baseline,measurements)
    write_json(output/'result.json',result)
    return result
