-- Discworld footprint proof: ordinary rectangular storage, circular playable domain.
-- This is an original schematic geography, not a reproduction of a published map.
-- Exterior plots stay allocated for engine indexing and carry an impassable feature.
include "MapEnums"
include "MapUtilities"
include "MountainsCliffs"
include "RiversLakes"
include "ResourceGenerator"
include "AssignStartingPlots"

local W,H = 48,56;
local R = 21.5;
local function Position(x,y)
  -- Odd rows are offset half a hex. Distances are in horizontal centre spacings.
  return x + (y % 2)*0.5 - (W-0.5)/2, (y-(H-1)/2)*math.sqrt(3)/2;
end
local function Radius(x,y)
  local a,b=Position(x,y); return math.sqrt(a*a+b*b);
end
function GetMapInitData(size)
  return {Width=W,Height=H,WrapX=false};
end

function GenerateMap()
  W,H=Map.GetGridSize();
  local void=assert(GameInfo.Features.FEATURE_DISC_VOID).Index;
  local land,rad={},{};
  local terrain={};
  local forest=GameInfo.Features.FEATURE_FOREST.Index;
  local jungle=GameInfo.Features.FEATURE_JUNGLE.Index;
  local ice=GameInfo.Features.FEATURE_ICE.Index;
  print("DISC_GENERATE_BEGIN",W,H,R);
  -- Low-frequency waves make a coherent central continent and separated islands.
  for y=0,H-1 do for x=0,W-1 do
    local i=y*W+x; local a,b=Position(x,y); local r=Radius(x,y);
    local theta=math.atan2(b,a);
    local edge=12.8+2.5*math.sin(3*theta+0.3)+1.4*math.cos(5*theta-0.4);
    local coast=0.65*math.sin(x*1.1+y*0.7)+0.45*math.cos(y*1.3-x*0.4);
    local central=r<edge+coast;
    -- Two offshore islands provide naval routes without closing the Rim Ocean.
    local island=((a-13.5)^2/12+(b+9.5)^2/8<1) or ((a+14)^2/7+(b-10)^2/12<1);
    land[i]=(central or island) and r<R-2.0; rad[i]=r;
    local t=g_TERRAIN_TYPE_OCEAN;
    if land[i] then
      if r<3.7 then t=g_TERRAIN_TYPE_SNOW_MOUNTAIN;
      elseif r<5 then t=g_TERRAIN_TYPE_SNOW_HILLS;
      elseif r<6.5 then t=g_TERRAIN_TYPE_TUNDRA;
      elseif b < -3 and a>0 and r>9 then t=g_TERRAIN_TYPE_DESERT;
      elseif math.sin(x*0.4)+math.cos(y*0.5)>0.2 then t=g_TERRAIN_TYPE_PLAINS;
      else t=g_TERRAIN_TYPE_GRASS; end
      if r>=6.5 and TerrainBuilder.GetRandomNumber(100,"Disc hills")<22 then t=t+1; end
    end
    terrain[i]=t; TerrainBuilder.SetTerrainType(Map.GetPlotByIndex(i),t);
  end end
  -- Paint coasts after the complete land mask exists; reserve the entire exterior.
  local nVoid=0;
  for i=0,W*H-1 do
    local p=Map.GetPlotByIndex(i);
    if not land[i] then
      for d=0,5 do local q=Map.GetAdjacentPlot(p:GetX(),p:GetY(),d);
        if q and land[q:GetIndex()] then TerrainBuilder.SetTerrainType(p,g_TERRAIN_TYPE_COAST);break;end
      end
    end
    if rad[i]>=R then
      TerrainBuilder.SetFeatureType(p,void); nVoid=nVoid+1;
    end
  end
  AreaBuilder.Recalculate(); TerrainBuilder.StampContinents();
  AddRivers();
  -- Radial climate avoids the stock generator's north/south ice bands.
  for i=0,W*H-1 do
    local p=Map.GetPlotByIndex(i); local r=rad[i];
    if land[i] and not p:IsMountain() and p:GetFeatureType()==-1 then
      local f=(r>10 and p:GetY()>H/2) and jungle or forest;
      if TerrainBuilder.GetRandomNumber(100,"Disc vegetation")<34 and TerrainBuilder.CanHaveFeature(p,f) then
        TerrainBuilder.SetFeatureType(p,f);
      end
    end
  end
  TerrainBuilder.AnalyzeChokepoints();
  ResourceGenerator.Create({resources=2,START_CONFIG=2});
  AssignStartingPlots.Create({MIN_MAJOR_CIV_FERTILITY=100,MIN_MINOR_CIV_FERTILITY=25,
    MIN_BARBARIAN_FERTILITY=1,START_MIN_Y=0,START_MAX_Y=0,START_CONFIG=2,STARTALLONLAND=true});
  AddGoodies(W,H);
  -- Final audit catches utility passes that might have altered the protected exterior.
  for i=0,W*H-1 do if rad[i]>=R then
    local p=Map.GetPlotByIndex(i);
    assert(p:GetFeatureType()==void and p:IsImpassable(),"Disc exterior overwritten");
    assert(p:GetResourceType()==-1,"Resource outside disc");
  end end
  print("DISC_GENERATE_COMPLETE",W,H,nVoid);
end
