-- Six unfinished Quarters retain their individual design-page material rules.
-- Bakers/Tailors resolve loaded classes; active nonofficial resource tags augment
-- the other six without inheriting mismatching vanilla mappings from SQL stubs.
CSC_MaterialMapDefinitions = {};
local D=CSC_MaterialMapDefinitions;
D.Design = {BAKERS={base={resources={"RESOURCE_BANANAS","RESOURCE_CATTLE","RESOURCE_MAIZE","RESOURCE_RICE","RESOURCE_WHEAT","RESOURCE_CSC_FLAX"}},spec={resources={"RESOURCE_COCOA","RESOURCE_COFFEE","RESOURCE_WINE","RESOURCE_HONEY","RESOURCE_OLIVES","RESOURCE_SALT","RESOURCE_SPICES","RESOURCE_SUGAR","RESOURCE_TEA"}}},TAILORS={base={resources={"RESOURCE_COTTON","RESOURCE_SHEEP","RESOURCE_CSC_FLAX"}},spec={resources={"RESOURCE_DYES","RESOURCE_SILK","RESOURCE_SILVER"}}},APOTHECARIES={base={resources={"RESOURCE_COCOA","RESOURCE_COFFEE","RESOURCE_HONEY","RESOURCE_INCENSE","RESOURCE_OLIVES","RESOURCE_SPICES","RESOURCE_TEA","RESOURCE_TOBACCO"}},spec={resources={"RESOURCE_COPPER","RESOURCE_IRON","RESOURCE_MERCURY","RESOURCE_SILVER"}}},STONEMASONS={base={resources={"RESOURCE_STONE"},hills=true},spec={resources={"RESOURCE_GYPSUM","RESOURCE_MARBLE"}}},CARPENTERS={base={resources={"RESOURCE_COPPER","RESOURCE_IRON"},features={"FEATURE_FOREST","FEATURE_JUNGLE"}},spec={resources={"RESOURCE_ALUMINUM","RESOURCE_AMBER","RESOURCE_DYES","RESOURCE_SILK","RESOURCE_SILVER"}}},BLACKSMITHS={base={resources={"RESOURCE_COPPER","RESOURCE_IRON"},hills=true},spec={resources={"RESOURCE_ALUMINUM","RESOURCE_SILVER"}}},GOLDSMITHS={base={resources={"RESOURCE_AMBER","RESOURCE_SILVER"}},spec={resources={"RESOURCE_DIAMONDS","RESOURCE_JADE"}}},BREWERS={base={resources={"RESOURCE_BANANAS","RESOURCE_WINE","RESOURCE_MAIZE","RESOURCE_RICE","RESOURCE_WHEAT"}},spec={resources={"RESOURCE_CITRUS","RESOURCE_COCOA","RESOURCE_COFFEE","RESOURCE_HONEY","RESOURCE_SPICES","RESOURCE_SUGAR"}}}};
local official = {RESOURCE_BANANAS=true,RESOURCE_CATTLE=true,RESOURCE_COPPER=true,RESOURCE_CRABS=true,RESOURCE_DEER=true,RESOURCE_FISH=true,RESOURCE_RICE=true,RESOURCE_SHEEP=true,RESOURCE_STONE=true,RESOURCE_WHEAT=true,RESOURCE_CITRUS=true,RESOURCE_COCOA=true,RESOURCE_COFFEE=true,RESOURCE_COTTON=true,RESOURCE_DIAMONDS=true,RESOURCE_DYES=true,RESOURCE_FURS=true,RESOURCE_GYPSUM=true,RESOURCE_INCENSE=true,RESOURCE_IVORY=true,RESOURCE_JADE=true,RESOURCE_MARBLE=true,RESOURCE_MERCURY=true,RESOURCE_PEARLS=true,RESOURCE_SALT=true,RESOURCE_SILK=true,RESOURCE_SILVER=true,RESOURCE_SPICES=true,RESOURCE_SUGAR=true,RESOURCE_TEA=true,RESOURCE_TOBACCO=true,RESOURCE_TRUFFLES=true,RESOURCE_WHALES=true,RESOURCE_WINE=true,RESOURCE_JEANS=true,RESOURCE_PERFUME=true,RESOURCE_COSMETICS=true,RESOURCE_TOYS=true,RESOURCE_CINNAMON=true,RESOURCE_CLOVES=true,RESOURCE_ALUMINUM=true,RESOURCE_COAL=true,RESOURCE_HORSES=true,RESOURCE_IRON=true,RESOURCE_NITER=true,RESOURCE_OIL=true,RESOURCE_URANIUM=true,RESOURCE_ANTIQUITY_SITE=true,RESOURCE_SHIPWRECK=true,RESOURCE_AMBER=true,RESOURCE_OLIVES=true,RESOURCE_TURTLES=true,RESOURCE_MAIZE=true,RESOURCE_HONEY=true};
function D.Resolve()
    -- The implemented Quarters use live SQL/ModSupport tags as their resource
    -- authority. D.Design alone must not revive resources disabled by settings.
    local out={};
    for _,q in ipairs(CSC_MaterialMapCore.Quarters) do
        out[q]={};
        for _,kind in ipairs({'base','spec'}) do
            local rule=D.Design[q][kind];local resources={};
            if q~='BAKERS' and q~='TAILORS' then
                for _,r in ipairs(rule.resources or {}) do if GameInfo.Resources[r] then resources[r]=true;end;end
            end
            local tag='CLASS_CSC_'..q..'_'..(kind=='base' and 'BASE' or 'SPEC');
            for row in GameInfo.TypeTags() do if row.Tag==tag and GameInfo.Resources[row.Type] then
                if q=='BAKERS' or q=='TAILORS' or not official[row.Type] then resources[row.Type]=true;end
            end;end
            local values={};for r in pairs(resources) do values[#values+1]=r;end;table.sort(values);
            out[q][kind]={resources=values,hills=rule.hills,features=rule.features};
        end
    end
    return out;
end
