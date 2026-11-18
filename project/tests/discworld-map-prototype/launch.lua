-- Isolated test setup; caller archives enabled-mod preferences before this command.
local disable={};local chosen;
for _,m in ipairs(Modding.GetInstalledMods()) do
  if m.Source=='Mod' and not m.Official then
    if m.Id=='98e2f456-2236-4bb9-a76c-4fe7cc928108' then chosen=m.Handle;
    elseif m.Enabled then disable[#disable+1]=m.Handle;end
  end
end
assert(chosen,'Disc prototype not discovered');
if #disable>0 then Modding.DisableMod(disable);end
Modding.EnableMod(chosen,true);
print('DISC_PACKAGE_ENABLED');
