"""Run the former Quarter cap against the exact revised installed package.

This diagnostic uses the game controller's existing CSC gameplay context.
Only the cap ordering changes. The revised quote is evaluated on the same
facts for the score log and is never published by this control.
"""

import re

from driver import parse, read, require


ADAPTER = 'Lua_UI/AI/CSC_AI_EconomyAdapters.lua'


def legacy_cap_script(adapter):
    scorer = re.search(r'^function E\.PlacementValue\(.*?^end$', adapter, re.M | re.S)
    fraction = re.search(r'^local MINIMUM_SITING_REFERENCE_FRACTION=(\.\d+)$', adapter, re.M)
    require(scorer and fraction, 'The pinned Quarter scorer signature changed')
    revised = 'proposed=strongLayout and math.min(ordinary,qualityCap)+spatial or ordinaryBid'
    require(scorer[0].count(revised) == 1, 'The pinned scorer no longer has the expected revised cap')
    # The former cap included both siting and land costs before clipping.
    # Below the cap the footprint is added back by the unchanged next line.
    legacy = scorer[0].replace(revised,
        'proposed=math.min(ordinary+spatial+footprint,qualityCap)-footprint')
    return f'''
local E=assert(CSC_AI_EconomyAdapters)
assert(E.AnchoredConnectionsEnabled and E.AnchoredConnectionAuditEnabled)
assert(Game.GetCurrentGameTurn()==1 and not CSC_QUARTER_CAP_CONTROL)
local revised=assert(E.PlacementValue)
local quotePlacement=assert(E.QuotePlacement)
local MINIMUM_SITING_REFERENCE_FRACTION={fraction[1]}
{legacy}
function E.QuotePlacement(snapshot,city,plot,profile,geometry,frontier,invoice,protection,ignored,covers,protected)
    local evaluated=quotePlacement(snapshot,city,plot,profile,geometry,frontier,invoice,protection,ignored,covers,protected)
    if evaluated.quote and evaluated.site and evaluated.parts then
        local candidate=revised(evaluated.quote,evaluated.site,protection,covers)
        if candidate~=evaluated.bid then
            local quote=evaluated.quote
            print(string.format('CSC_QUARTER_CAP_AB turn=%d player=%d city=%d district=%d plot=%d strong=%s legacyQ8=%d revisedQ8=%d footprintQ8=%d',
                Game.GetCurrentGameTurn(),snapshot.id,city:GetID(),profile.district.Index,plot:GetIndex(),
                tostring(evaluated.parts.strongLayout~=nil),evaluated.bid,candidate,
                (quote.footprintBidQ8 or quote.siteAdjustmentQ8 or 0)-evaluated.parts.penaltyQ8))
        end
    end
    return evaluated
end
CSC_QUARTER_CAP_CONTROL=true
print('CSC_QUARTER_CAP_CONTROL_READY')
'''


def install(controller, out, package):
    # CSC publishes on context startup. Turn 1 has no Quarter bids in the
    # treatment. Require the same empty packet before switching the scorer.
    raw = controller.cmd('print("CSC_CAP_STATUS="..CE_AIDistrictScoresStatus())',
                         'GameCore_Tuner', 'quarter-cap-control-empty-opening')
    status = parse(raw, 'CSC_CAP_STATUS')
    require(status['ready'] == status['version'] == 1 and status['entries'] == 0
            and status['faults'] == 0, 'The legacy cap must start before the first scored packet')
    command = legacy_cap_script(read(package / ADAPTER))
    (out / 'quarter-cap-control.lua').write_text(command, encoding='utf-8')
    raw = controller.cmd(command, 'CSC_AI_BakersGameplay', 'install-legacy-quarter-cap-control')
    require('CSC_QUARTER_CAP_CONTROL_READY' in raw, 'The legacy cap did not acknowledge installation')
