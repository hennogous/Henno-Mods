"""Measure a city-specific Workshop adjacency through Civ's stock plot previews."""
import re

from driver import HERE, lua, read, require, write_json


def observe_city_cue(controller, folder, seats, turn, allow_fallback):
    setup='local CSC_CUE_SEATS='+lua(list(seats))+'\nlocal CSC_CUE_ALLOW_FALLBACK='+lua(allow_fallback)
    pair = controller.cmd('\n'.join((setup,read(HERE/'city_material_cue_choice.lua'),
                          read(HERE/'city_material_cue_sites.lua'),read(HERE/'city_material_cue_probe.lua'))),
                          'PlotInfo',f'city-cue-select-{turn}')
    if 'CSC_NATIVE_CUE_NO_PAIR' in pair:
        return False
    match = re.search(r'CSC_NATIVE_CUE_PAIR\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
                      r'\s+(\d+)\s+(\d+)\s+(MOD_CSC_AI_LOCAL_CUE_\w+)\s+([\d.-]+)\s+([\d.-]+)'
                      r'\s+(\d+)\s+(-?\d+)\s+(\d+)\s+([01])',pair)
    require(match is not None,'Missing stock preview pair')
    player,city,district,a,b,count_a,count_b=map(int,match.groups()[:7])
    modifier=match[8]
    base=[float(match[9]),float(match[10])]
    cutoff,hits,total,exact=map(int,match.groups()[10:])
    preamble=f"""local city=assert(CityManager.GetCity({player},{city}))
local plot=assert(Map.GetPlot(city:GetX(),city:GetY()))
"""
    def change(label,statement):
        controller.cmd(preamble+statement,'GameCore_Tuner','city-cue-'+label)

    def preview(label):
        raw=controller.cmd(f"""local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index
print('CSC_NATIVE_CUE_READ',Map.GetPlotByIndex({a}):GetAdjacencyYield({player},{city},{district},y),
    Map.GetPlotByIndex({b}):GetAdjacencyYield({player},{city},{district},y))""",'PlotInfo','city-cue-read-'+label)
        values=re.search(r'CSC_NATIVE_CUE_READ\s+([\d.-]+)\s+([\d.-]+)',raw)
        require(values is not None,'Missing stock adjacency readback')
        return list(map(float,values.groups()))

    prop='CSC_AI_LOCAL_CUE_PROBE'
    samples={'before':base}
    try:
        change('attach',f"city:AttachModifierByID('{modifier}')")
        samples['attached']=preview('attached')
        change('enable',f"plot:SetProperty('{prop}',1)")
        samples['plot_enabled']=preview('plot-enabled')
        change('switch',f"plot:SetProperty('{prop}',0)\ncity:SetProperty('{prop}',1)")
        samples['city_enabled']=preview('city-enabled')
    finally:
        change('clear',f"city:SetProperty('{prop}',0)\nplot:SetProperty('{prop}',0)")
    samples['cleared']=preview('cleared')
    # The independent positive control is deliberately last. Attaching it in
    # this disposable no-CE game does not require any detach API or affect a
    # qualification save. A failed gate still yields a useful diagnostic.
    change('positive-control',f"city:AttachModifierByID('{modifier}_ALWAYS')")
    samples['unconditional']=preview('unconditional')
    expected=[base[0]+7*count_a,base[1]+7*count_b]
    change('terrain-cutoff',f"city:AttachModifierByID('{modifier}_COUNT_{cutoff}')")
    samples['threshold']=preview('terrain-cutoff')
    delta=[after-before for after,before in zip(samples['threshold'],samples['unconditional'])]
    write_json(folder/'city-cue-result.json',dict(turn=turn,player=player,city=city,district=district,
        plots=[a,b],terrain_counts=[count_a,count_b],modifier=modifier,expected=expected,readbacks=samples,
        cutoff=cutoff,eligible_sites=total,sites_rewarded=hits if exact else None,exact_base=bool(exact),
        threshold_delta=delta,threshold_prediction=[count_a//cutoff,count_b//cutoff],
        positive_control=samples['unconditional']==expected,restored=samples['cleared']==base,
        plot_gate=samples['plot_enabled']==expected,city_gate=samples['city_enabled']==expected))
    return True
