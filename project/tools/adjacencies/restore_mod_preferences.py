"""Restore the mod preferences captured before the CSC-only live fixture.

Run at the main menu after testing. Resolves fresh native mod handles by ID;
does not write the mod database or restore the old installed CSC package.
"""
import argparse
import json
from pathlib import Path
import tuner


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preferences',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--port',type=int,default=4318)
    args=parser.parse_args()
    prefs=json.loads(args.preferences.read_text(encoding='utf-8'))
    assert prefs and all(isinstance(value,bool) for value in prefs.values())
    tuner.PORT=args.port
    states=tuner.states()
    assert 'MainMenu' in states,'Restore at the main menu, outside the test game'
    entries=','.join('['+json.dumps(key)+']='+str(value).lower() for key,value in prefs.items())
    code='''local wanted={%s}; local mods=Modding.GetInstalledMods(); local disable={};
for _,mod in ipairs(mods) do if wanted[mod.Id]==false and mod.Enabled then disable[#disable+1]=mod.Handle; end end
if #disable>0 then Modding.DisableMod(disable); end
for _,mod in ipairs(mods) do if wanted[mod.Id]==true then Modding.EnableMod(mod.Handle,true); end end
local mismatches={}; local count=0;
for _,mod in ipairs(Modding.GetInstalledMods()) do
 if wanted[mod.Id]~=nil then count=count+1; if mod.Enabled~=wanted[mod.Id] then mismatches[#mismatches+1]=mod.Id; end end
end
assert(#mismatches==0,'Mod preferences differ: '..table.concat(mismatches,','));
print('CSC_MOD_PREFERENCES_RESTORED',count);
'''%entries
    messages=tuner.command(code,states['MainMenu'],2)
    text='\n'.join(messages)
    args.output.write_text(text+'\n',encoding='utf-8')
    assert 'ERR:' not in text and 'CSC_MOD_PREFERENCES_RESTORED' in text,text
    print('Restored original mod preferences; installed CSC test package retained.')


if __name__=='__main__': main()
