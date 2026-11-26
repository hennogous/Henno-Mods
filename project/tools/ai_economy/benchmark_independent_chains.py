"""Offline marginal Quarter forecast with increasing numbers of unrelated chains.

Each incumbent has its own city, working buildings and customer. The new
Quarter shares no queue, building, route or payout with them. This control
lets us increase empire size while holding the candidate's value constant.
The production Lua runs with the existing test fixture's deterministic price.
"""

from statistics import median
from time import perf_counter

from test_joint_customer_economy import JointEconomy


def main():
    vm = JointEconomy().vm()
    prepare = vm.eval('''function(n)
        local incumbents,admitted={},{}
        for i=1,n do
            local site=chain('fixed'..i,i)
            local buyer=venue(100+i,i)
            buyer.working=true
            site.customers={buyer}
            incumbents[i]=site
            admitted[site]=true
        end
        local base=assert(M.JointForecast(world(incumbents),price))
        local candidate=chain('candidate',1000)
        candidate.existing=false
        candidate.seconds={{type='MILL',turns=3,unlock=0,cost=10,terrain=1}}
        candidate.third=nil
        candidate.suppliers={{kind='base',plot=9000,city=1000,ready=1,worked=true}}
        local sites=copy(incumbents)
        sites[#sites+1]=candidate
        local after=world(sites)
        after.baselinePlan=base.plan
        after.affectedChains={candidate=true}
        after.firstChainKey='candidate'
        return function(repeats,reuse)
            local calls=0
            local function counted(s,h) calls=calls+1;return price(s,h) end
            local result
            for i=1,repeats do result=assert(M.JointForecast(after,counted,reuse and admitted or nil)) end
            return result.valueQ8-base.valueQ8, result.evaluations, calls/repeats
        end
    end''')
    reference = None
    for n in (1, 4, 8, 16):
        run = prepare(n)
        delta, evaluations, calls = run(1, False)
        if reference is None:
            reference = delta, evaluations
        assert (delta, evaluations) == reference
        samples = {False: [], True: []}
        assert run(1, True)[:2] == (delta, evaluations)
        reused = run(1, True)
        assert reused[:2] == (delta, evaluations) and reused[2] < calls
        for batch in range(7):
            for reuse in (False, True) if batch % 2 == 0 else (True, False):
                start = perf_counter()
                assert run(25, reuse) == (reused if reuse else (delta, evaluations, calls))
                samples[reuse].append((perf_counter() - start) * 1000 / 25)
        print(f'{n:2} incumbents  {evaluations:2} visits  {calls:4.0f}/{reused[2]:.0f} prices  '
              f'{delta:8} marginal Q8  {median(samples[False]):.3f} full / '
              f'{median(samples[True]):.3f} reused ms/forecast')


if __name__ == '__main__':
    main()
