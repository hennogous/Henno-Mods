-- Remove only this test's unit and restore the technology flag it changed.
local a=assert(Game:GetProperty('DISC_NAVAL_FIXTURE'));
local u=Players[0]:GetUnits():FindID(a[1]);if u then UnitManager.Kill(u);end
local had=Game:GetProperty('DISC_TEST_HAD_CARTOGRAPHY');assert(had~=nil);
Players[0]:GetTechs():SetTech(GameInfo.Technologies.TECH_CARTOGRAPHY.Index,had);
Game:SetProperty('DISC_NAVAL_FIXTURE',nil);
Game:SetProperty('DISC_TEST_HAD_CARTOGRAPHY',nil);
print('DISC_NAVAL_FIXTURE_REMOVED');
