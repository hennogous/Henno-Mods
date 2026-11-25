"""Generate a diagnostic-only overlay for one Quarter and one frontier plot.

This observes the established Quarter's normal shortlist and then prices its
frontier option and all viable backups, including rows the shortlist skipped.
The additional quotes occur after the connection planner makes its decisions.
The overlay submits no bids, changes no saved plan and leaves the visit budget
and production selection intact.
"""

import argparse
from pathlib import Path


APPRAISAL = '''
    if pid==PLAYER and turn>=FIRST and turn<=LAST then
        local actual={}
        for _,plan in ipairs(plans)do
            if plan.order=='quarterFirst' and plan.anchor==ANCHOR then actual[plan.stage]=plan end
        end
        local stages={0,2,3,4}
        local inspected=0
        for _,stage in ipairs(stages)do
            local key=table.concat({'quarterFirst',ANCHOR,stage,'QUARTER'},':')
            local group=groups.quarterFirst[key]
            local target=group and group.plots[FRONTIER]
            if target then
                for _,option in ipairs(target.options)do
                    if option.purchaseGold and option.city==BUYER and option.district==DISTRICT then
                        local slotWait
                        if type(customerPurchaseWait)=='function' then slotWait=customerPurchaseWait(option) end
                        local paid={plot=FRONTIER,option=option,valueQ8=value(option,slotWait)}
                        local ready=snapshot.ConnectionDistrictTurns(option.city,option.district)
                        local net=ready and snapshot.CustomerNetValue
                            and snapshot.CustomerNetValue(option.city,option.district,option.plot,ready+(slotWait or 0))
                        local buyer=snapshot.cities[option.city]
                        local capacity=buyer and snapshot.DistrictCapacity and snapshot.DistrictCapacity(buyer.object)
                        local ownedCount,otherCount,unknown,bestOwned,bestAlternative=0,0,0,nil,nil
                        for alternativePlot,row in pairs(group.plots)do
                            if alternativePlot~=FRONTIER then for _,backup in ipairs(row.options)do
                                    if backup.purchaseGold then otherCount=otherCount+1 else ownedCount=ownedCount+1 end
                                    local comparableWait=backup.city==option.city and backup.district==option.district
                                        and slotWait or nil
                                    local quote=value(backup,comparableWait)
                                    if not quote then
                                        unknown=unknown+1
                                    elseif paid.valueQ8 then
                                        local comparable=competitiveBackup(paid,{plot=row.plot,option=backup,valueQ8=quote})
                                        bestAlternative=math.max(bestAlternative or 0,comparable)
                                        if not backup.purchaseGold then
                                            bestOwned=math.max(bestOwned or 0,comparable)
                                        end
                                    end
                                    print(string.format('CSC_DIAGNOSTIC_CUSTOMER_BACKUP turn=%d player=%d anchor=%d stage=%d city=%d district=%d plot=%d invoice=%s valueQ8=%s',
                                        turn,pid,ANCHOR,stage,backup.city,backup.district,row.plot,
                                        tostring(backup.purchaseGold),tostring(quote)))
                            end end
                        end
                        local margin=paid.valueQ8 and unknown==0 and paid.valueQ8-(bestAlternative or 0) or nil
                        print(string.format('CSC_DIAGNOSTIC_CUSTOMER_APPRAISAL turn=%d player=%d anchor=%d stage=%d city=%d district=%d plot=%d invoice=%d paidQ8=%s nativeSiteQ8=%s used=%d allowed=%d owned=%d otherFrontier=%d unknown=%d comparableOwnedQ8=%s marginQ8=%s actualPlot=%s actualPurchaseCreditQ8=%s nextSlotTurns=%s appraisalWait=%s',
                            turn,pid,ANCHOR,stage,option.city,option.district,option.plot,option.purchaseGold,
                            tostring(paid.valueQ8),tostring(net),capacity and capacity.used or -1,
                            capacity and capacity.allowed or -1,ownedCount,otherCount,unknown,
                            tostring(bestOwned),tostring(margin),tostring(actual[stage] and actual[stage].best.plot),
                            tostring(actual[stage] and actual[stage].purchaseCreditQ8),
                            tostring(capacity and capacity.nextSlotTurns),tostring(slotWait)))
                        inspected=inspected+1
                    end
                end
            end
        end
        if inspected==0 then
            print(string.format('CSC_DIAGNOSTIC_CUSTOMER_APPRAISAL_MISSING turn=%d player=%d anchor=%d city=%d district=%d plot=%d',
                turn,pid,ANCHOR,BUYER,DISTRICT,FRONTIER))
        end
    end
'''


def instrument(adapter, *, first, last, player, anchor, quarter, buyer, district, frontier):
    if not 0 <= last-first <= 10 or quarter not in ('BAKERS', 'TAILORS'):
        raise ValueError('Require a short appraisal window for Bakers or Tailors')
    targets = dict(FIRST=first, LAST=last, PLAYER=player, ANCHOR=anchor, QUARTER=quarter,
                   BUYER=buyer, DISTRICT=district, FRONTIER=frontier)
    probe = APPRAISAL
    for name, value in targets.items():
        probe = probe.replace(name, str(value))
    anchor_line = '    connectionMemory[pid]=nextMemory\n    return plans'
    if adapter.count(anchor_line) != 1:
        raise ValueError('Appraisal anchor changed')
    return adapter.replace(anchor_line, probe + anchor_line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('adapter', type=Path)
    parser.add_argument('destination', type=Path)
    for name in ('first', 'last', 'player', 'anchor', 'buyer', 'district', 'frontier'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--quarter', choices=('BAKERS', 'TAILORS'), required=True)
    args = vars(parser.parse_args())
    adapter, destination = args.pop('adapter'), args.pop('destination')
    content = instrument(adapter.read_text(encoding='utf-8'), **args)
    with destination.open('x', encoding='utf-8') as output:
        output.write(content)


if __name__ == '__main__':
    main()
