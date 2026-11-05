-- Exactly one fresh controlled world. The shared host reserves this operation
-- before transmission and never repeats it after an ambiguous acknowledgement.
GameConfiguration.SetToDefaults()
GameConfiguration.SetRuleSet('RULESET_EXPANSION_2')
BuildHeadlessGameSetup()
RebuildPlayerParameters(true)
GameSetup_RefreshParameters()
MapConfiguration.SetScript('Continents.lua')
MapConfiguration.SetMapSize('MAPSIZE_SMALL')
GameConfiguration.SetParticipatingPlayerCount(6)
GameConfiguration.SetValue('CITY_STATE_COUNT',9)
GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE')
GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE')
GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',26131105)
MapConfiguration.SetValue('RANDOM_SEED',16131105)
MapConfiguration.SetValue('resources',2)
GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false)
GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'))
-- Fixed identities avoid random leader traits such as a free human Monument
-- violating the two bare Mill-city fixture contract. Names are verified against
-- the shipped Base/Assets/Gameplay/Data/Leaders.xml.
local leaders={'LEADER_CLEOPATRA','LEADER_GANDHI','LEADER_TOMYRIS',
    'LEADER_T_ROOSEVELT','LEADER_VICTORIA','LEADER_HOJO'}
for i,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do
    assert(leaders[i],'Unexpected participant count')
    PlayerConfigurations[pid]:SetLeaderTypeName(leaders[i])
end
ReleasePlayerParameters()
HideGameSetup()
Automation.SetAutoStartEnabled(true)
Network.HostGame(ServerType.SERVER_TYPE_NONE)
