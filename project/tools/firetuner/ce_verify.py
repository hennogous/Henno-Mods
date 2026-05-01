import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ft_utils import FTSession

ft = FTSession()
ft.connect()

# Check if that spearman is still on the map (valid coords) or gone
lines = ft.q(
    "local p=Players[63]; local found=false; "
    "for i,u in p:GetUnits():Members() do "
    "if u:GetID()==851980 then "
    "found=true; "
    "print('UNIT:x='..u:GetX()..':y='..u:GetY()..':hp='..(u:GetMaxDamage()-u:GetDamage())) "
    "end end; "
    "if not found then print('UNIT:NOT_IN_LIST') end",
    wait=3.0
)
for l in lines: print(l)

# Also: how many barb spearmen are still alive at turn 149 area?
lines2 = ft.q(
    "local count=0; "
    "for i=0,63 do local p=Players[i]; "
    "if p and p:IsAlive() and p:IsBarbarian() then "
    "for j,u in p:GetUnits():Members() do "
    "local ui=GameInfo.Units[u:GetType()]; "
    "if u:GetX()>0 then count=count+1 end "
    "end end end; "
    "print('LIVE_BARBS:'..count)",
    wait=3.0
)
for l in lines2: print(l)

ft.close()
