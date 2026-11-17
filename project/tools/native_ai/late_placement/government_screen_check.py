"""One UI-only check at a shared-controller inactive boundary.

Open Government/Policies and close them through their own callbacks. Never
select cards/governments, grant civics, issue game orders or advance turns.
"""
import json
from pathlib import Path
import time


class GovernmentScreenCheck:
    def __init__(self,controller,output,user_root):
        self.controller=controller;self.output=Path(output);self.user_root=Path(user_root);self.done=False
        (self.output/'government_screen_check.py').write_bytes(Path(__file__).read_bytes())

    def __call__(self,turn):
        if self.done or turn<25:return
        self.done=True
        log=self.user_root/'Logs/Lua.log';offset=log.stat().st_size;parts=[]
        try:
            parts.append(self.controller.cmd('''
assert(Game.GetLocalPlayer()==0,'Government check requires the inactive observer');
assert(ExposedMembers.RMA and type(ExposedMembers.RMA.CalculateModifierEffect)=='function','Missing original RMA API');
local ok,problem=xpcall(OnOpenGovernmentScreenMyGovernment,debug.traceback);
print('CSC_GOVERNMENT_OPEN',tostring(ok),tostring(ContextPtr:IsHidden()),tostring(problem));
''','GovernmentScreen','regression-open-government'))
            if 'CSC_GOVERNMENT_OPEN\ttrue\tfalse'not in parts[-1]:
                raise RuntimeError('Government page did not open; see UI check transcript')
            time.sleep(1)
            parts.append(self.controller.cmd('''
local ok,problem=xpcall(OnOpenGovernmentScreenPolicies,debug.traceback);
print('CSC_POLICIES_OPEN',tostring(ok),tostring(ContextPtr:IsHidden()),tostring(problem));
''','GovernmentScreen','regression-open-policies'))
            if 'CSC_POLICIES_OPEN\ttrue\tfalse'not in parts[-1]:
                raise RuntimeError('Policies page did not open; see UI check transcript')
            time.sleep(1)
        finally:
            # Always attempt normal cleanup of this unedited page.
            parts.append(self.controller.cmd('''
local ok,problem=xpcall(Close,debug.traceback);
print('CSC_GOVERNMENT_CLOSED',tostring(ok),tostring(ContextPtr:IsHidden()),tostring(problem));
''','GovernmentScreen','regression-close-government'))
            (self.output/'government-screen-check.txt').write_text('\n'.join(parts),encoding='utf-8')
        time.sleep(.5)
        with log.open('rb')as file:
            file.seek(offset);delta=file.read().decode('utf-8-sig',errors='replace')
        (self.output/'government-screen-check-lua.log').write_text(delta,encoding='utf-8')
        if 'Runtime Error:'in delta or 'CSC_GOVERNMENT_CLOSED\ttrue\ttrue'not in parts[-1]:
            raise RuntimeError('Government screen UI regression; see captured Lua delta')
        if 'CSC policy estimates: attached to original BRS analysis API'not in log.read_text(encoding='utf-8-sig',errors='replace'):
            raise RuntimeError('CSC policy adapter did not confirm attachment')
        (self.output/'government-screen-check.json').write_text(json.dumps(dict(
            verified=True,turn=turn,government_open=True,policies_open=True,
            closed=True,gameplay_orders=False,scope='inactive observer0 UI only'),indent=2)+'\n',encoding='utf-8')
