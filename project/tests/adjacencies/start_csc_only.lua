-- Run from the main-menu FireTuner state. Creates a new disposable test game.
-- Prints the original enabled mod IDs so preferences can be restored later.
local entries={};
local disable={};
local csc=nil;
for _,mod in ipairs(Modding.GetInstalledMods()) do
    if mod.Source=='Mod' and not mod.Official then
        entries[#entries+1]='"'..mod.Id..'":'..tostring(mod.Enabled);
        if mod.Id=='c5e66bd1-d804-443b-ac3d-1917a20dba3c' then csc=mod.Handle;
        elseif mod.Enabled then disable[#disable+1]=mod.Handle; end
    end
end
print('CSC_MOD_PREFS={'..table.concat(entries,',')..'}');
if #disable>0 then Modding.DisableMod(disable); end
assert(csc,'CSC test package is not installed');
Modding.EnableMod(csc,true);
-- Configuration APIs are absent in some frontend tuner states. In that case
-- HostGame uses the existing setup; inspect the resulting runtime DB explicitly.
if GameConfiguration and MapConfiguration then
    GameConfiguration.SetValue('RULESET','RULESET_EXPANSION_2');
    MapConfiguration.SetValue('MAP_SIZE','MAPSIZE_DUEL');
    MapConfiguration.SetValue('MAP_SCRIPT','Continents.lua');
    MapConfiguration.SetValue('RANDOM_SEED',314159);
    GameConfiguration.SetValue('RANDOM_SEED',271828);
    GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);
end
print('CSC_ONLY_STARTING');
Network.HostGame(-1);
