"""Build a diagnostic-only EconomyModel overlay for a short replay.

The shadow cache observes visits to successful states past the first 16 slots.
It never supplies a result to the search. Only candidate Quarter worlds are
sampled. The real search, prices, evaluation budget and bids stay in use.
"""

import argparse
from pathlib import Path


def instrument(model):
    def replace(old, new):
        nonlocal model
        if model.count(old) != 1:
            raise ValueError(f'Profiler anchor changed: {old}')
        model = model.replace(old, new)

    replace('local pricedStates,pricedCount={},0', '''local pricedStates,pricedCount={},0
    -- The generated replay overlay profiles Quarter objectives only.
    local probe=world.objective and variable and type(CE_AIMonotonicSeconds)=='function' and {
        overflow={},overflowCount=0,builds=0,priced=0,hits=0,reused=0,shadowHits=0,
        buildTime=0,priceTime=0,shadowTime=0
    }
    local clock=CE_AIMonotonicSeconds''')
    replace('if startingResult then return startingResult end', '''if startingResult then
            if probe then probe.reused=probe.reused+1 end
            return startingResult
        end''')
    replace('if pricedStates[pricedKey]then return pricedStates[pricedKey]end', '''if pricedStates[pricedKey] then
                if probe then probe.hits=probe.hits+1 end
                return pricedStates[pricedKey]
            end''')
    replace('local full=memo and memo.entries[key]', '''local evaluationStart=probe and (probe.buildTime+probe.priceTime)
        local full=memo and memo.entries[key]''')
    replace('local problem;full,problem=buildLedger(selected,disabled)', '''local started=probe and clock()
            local problem;full,problem=buildLedger(selected,disabled)
            if started then
                probe.builds=probe.builds+1
                probe.buildTime=probe.buildTime+clock()-started
            end''')
    # Limit the replacement to the search. The model also prices single-site ledgers.
    replace('''        local value,error=M.Price(result,price,horizon)
        if not value then return nil,error end
        result.valueQ8=value;result.servicesExcluded=not world.includeServices;result.modelOnly=true''', '''        local started=probe and clock()
        local value,error=M.Price(result,price,horizon)
        if not value then return nil,error end
        if started then
            probe.priced=probe.priced+1
            probe.priceTime=probe.priceTime+clock()-started
        end
        result.valueQ8=value;result.servicesExcluded=not world.includeServices;result.modelOnly=true''')
    replace('''            pricedStates[pricedKey]=result;pricedCount=pricedCount+1
        end''', '''            pricedStates[pricedKey]=result;pricedCount=pricedCount+1
        elseif probe then
            if probe.overflow[pricedKey] then
                probe.shadowHits=probe.shadowHits+1
                probe.shadowTime=probe.shadowTime+probe.buildTime+probe.priceTime-evaluationStart
            elseif probe.overflowCount<16 then
                probe.overflow[pricedKey]=true
                probe.overflowCount=probe.overflowCount+1
            end
        end''')
    replace('''    best.evaluations=evaluations;best.affectedChains=#sites''', '''    if probe then
        local function micros(seconds)return math.floor(seconds*1000000+.5)end
        print(string.format('CSC_DIAGNOSTIC_JOINT_SEARCH turn=%d chains=%d logical=%d reused=%d hits=%d builds=%d priced=%d shadowHits=%d buildMicros=%d priceMicros=%d shadowMicros=%d',
            Game.GetCurrentGameTurn(),#sites,evaluations,probe.reused,probe.hits,probe.builds,
            probe.priced,probe.shadowHits,micros(probe.buildTime),micros(probe.priceTime),micros(probe.shadowTime)))
    end
    best.evaluations=evaluations;best.affectedChains=#sites''')
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    content = instrument(args.model.read_text(encoding='utf-8'))
    with args.destination.open('x', encoding='utf-8') as output:
        output.write(content)


if __name__ == '__main__':
    main()
