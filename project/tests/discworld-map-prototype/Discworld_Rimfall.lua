-- Rimfall v0.1: a southern 60-degree VFX study, not terrain displacement.
-- Uses the same native AssetPreview API as Firaxis's TunerAssetPreviewPanel.
-- Preview instances are transient; this addin recreates them when a game loads.
-- No gameplay state, movement flags, or fog visibility is changed here.
local owned = {};
function Discworld_ClearRimfall()
  for _,id in ipairs(owned) do AssetPreview.Destroy(id); end
  owned = {};
end
function Discworld_CreateRimfall()
  if MapConfiguration.GetScript() ~= 'Discworld_Prototype.lua' then return; end
  if #owned > 0 then return; end
  local w,h=Map.GetGridSize();
  local ax,ay=UI.GridToWorld(0,0);local bx,by=UI.GridToWorld(w-1,h-1);
  local cx,cy=(ax+bx)/2,(ay+by)/2;
  local nx,ny=UI.GridToWorld(1,0);local spacing=nx-ax;
  -- GridToWorld returns uninitialized coordinates during UI construction.
  -- Wait for LoadGameViewStateDone; never populate native instances from them.
  if spacing<=0 or spacing>1000 or math.abs(cx)>1000000 or math.abs(cy)>1000000 then
    print('DISC_RIMFALL_WAITING_FOR_WORLD');return;
  end
  local function spawn(name,x,y,z,scale,angle)
    local id=AssetPreview.Create(name,x,y);
    if id and id>=0 then
      owned[#owned+1]=id;
      -- Fourth position argument was verified through GetInstanceInfoByID.
      -- Elevated emitters expose the falling particles above the flat sea.
      AssetPreview.SetInstancePosition(id,x,y,z);
      AssetPreview.SetInstanceScale(id,scale);
      AssetPreview.SetInstanceOrientation(id,angle);
    end
  end
  for degrees=240,300,0.8 do
    local a=math.rad(degrees);local dx,dy=math.cos(a),math.sin(a);
    local x,y=cx+21.35*spacing*dx,cy+21.35*spacing*dy;
    spawn('FX_Waterfall01',x,y,38,4,a+math.pi/2);
    spawn('FX_Waterfall03',x+18*dx,y+18*dy,10,3,a);
    spawn('FX_Waterfall07',x,y,24,3,a+math.pi/2);
  end
  print('DISC_RIMFALL_V01_INSTANCES',#owned);
end
Events.LoadGameViewStateDone.Add(Discworld_CreateRimfall);
-- For explicit FireTuner injection after the event, call CreateRimfall manually.
