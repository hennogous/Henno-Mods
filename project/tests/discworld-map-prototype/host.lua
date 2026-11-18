GameConfiguration.SetToDefaults();
GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');
BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();
MapConfiguration.SetScript('Discworld_Prototype.lua');
MapConfiguration.SetMapSize('MAPSIZE_TINY');
GameConfiguration.SetParticipatingPlayerCount(4);
GameConfiguration.SetValue('CITY_STATE_COUNT',4);
GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');
GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');
GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',10112026);
MapConfiguration.SetValue('RANDOM_SEED',10112026);
MapConfiguration.SetValue('resources',2);MapConfiguration.SetValue('start',2);
local names={'LEADER_TRAJAN','LEADER_CLEOPATRA','LEADER_GILGAMESH','LEADER_TOMYRIS'};
for i,id in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do
  PlayerConfigurations[id]:SetLeaderTypeName(names[i]);
end
ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);
print('DISC_HOST_REQUEST',MapConfiguration.GetScript());
Network.HostGame(ServerType.SERVER_TYPE_NONE);
