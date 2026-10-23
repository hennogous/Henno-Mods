-- Appended temporarily to the installed research context; source stays pristine.
CSC_RESEARCH_PROBE_NATIVE={version='clean-strategy-natural-decisions-v1',calls={},first_true={},errors={}}
GameEvents.CSC_TestResearchAlways.Add(function(pid,which)
 local R=CSC_RESEARCH_PROBE_NATIVE
 local key=tostring(pid)..':'..tostring(which)
 R.calls[key]=(R.calls[key] or 0)+1
 local active=pid>=1 and pid<=5 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman()
 if active and not R.first_true[key] then R.first_true[key]=Game.GetCurrentGameTurn() end
 return active
end)
print('CSC_TEST_RESEARCH_CALLBACKS_READY',CSC_RESEARCH_PROBE_NATIVE.version)
