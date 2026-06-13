"""
patch_mab.py -- Apply CSC customisations on top of a fresh MAB install.

Usage:
    python patch_mab.py [--dry-run] [--src <vanilla_dir>]

By default the script patches in-place the CSC copies in:
    .../Henno Mods/Civ Supply Chains/Lua_UI/Ruivo_Adjacencies/

Use --src <dir> to point at a fresh Ruivo workshop copy, then copy the
patched results back into your CSC project directory.

    python patch_mab.py --src "C:\\...\\workshop\\3429735059" --dry-run

What it patches
---------------
RUIVO_STAT_MODULE_GP.lua
  1. CallAdjacencyFunction     -- Rings -> iMinRings/iMaxRings;
                                  add FROM_RINGS_SPECIFIC_WONDER hook
  2. StatsModule_For_GP        -- Rings -> iMinRings/iMaxRings
  3. StatsModule_For_UI        -- Rings -> iMinRings/iMaxRings
  4. StatsModule_For_Display   -- Rings -> iMinRings/iMaxRings
  5. StatsModule_For_Display call site (row.Rings -> row.MinRings/MaxRings)
  6. Insert FROM_RINGS_SPECIFIC_WONDER function (after FROM_RINGS_WONDERS)

NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua
  7-9. All 3 StatsModule_For_GP call sites (row.Rings -> Min/Max)
"""

import sys, os, shutil, pathlib, io
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DRY_RUN = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# Resolve source directory
# ---------------------------------------------------------------------------
# Priority: --src flag > env var MAB_VANILLA_SRC > hardcoded default
MAB_DEFAULT = pathlib.Path(
    r"C:\Program Files (x86)\Steam\steamapps\workshop\content\289070\3429735059"
)
CSC_DEFAULT = pathlib.Path(
    r"C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI"
    r"\Henno Mods\Civ Supply Chains\Lua_UI\Ruivo_Adjacencies"
)

src_flag = None
for i, a in enumerate(sys.argv):
    if a == "--src" and i + 1 < len(sys.argv):
        src_flag = pathlib.Path(sys.argv[i + 1])
        break

SRC_DIR = src_flag or pathlib.Path(
    os.environ.get("MAB_VANILLA_SRC", "") or MAB_DEFAULT
)
TGT_DIR = CSC_DEFAULT  # only used for the default no-arg path

STAT_SRC = SRC_DIR / "RUIVO_STAT_MODULE_GP.lua"
GP_SRC   = SRC_DIR / "NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua"

# Target (where we write the patched files) -- same dir as source unless
# user passes a different --src; in practice they just copy vanilla in.
STAT_FILE = STAT_SRC
GP_FILE   = GP_SRC

# ---------------------------------------------------------------------------
# FROM_RINGS_SPECIFIC_WONDER function to insert
# ---------------------------------------------------------------------------
SPECIFIC_WONDER_FUNC = """
--============================================================================================================================
--  CSC CUSTOM: FROM_RINGS_SPECIFIC_WONDER
--  Returns 1 if a specific wonder (BuildingType string) is within iMinRings..iMaxRings
--  of the plot and owned by the player.
--  Uses GetPlotXYWithRangeCheck (Zegangani's approach).
--============================================================================================================================
function FROM_RINGS_SPECIFIC_WONDER(iX, iY, playerID, pCity, CustomAdjacentObject, iMinRings, iMaxRings)
    for dx = (iMaxRings * -1), iMaxRings do
        for dy = (iMaxRings * -1), iMaxRings do
            local pPlot = Map.GetPlotXYWithRangeCheck(iX, iY, dx, dy, iMaxRings)
            if pPlot then
                local iDistance = Map.GetPlotDistance(iX, iY, pPlot:GetX(), pPlot:GetY())
                if iDistance <= iMaxRings and iDistance >= iMinRings then
                    local eWonderType = pPlot:GetWonderType()
                    if eWonderType ~= -1 and pPlot:IsWonderComplete() and pPlot:GetOwner() == playerID then
                        if BuildingTypeMap[eWonderType] == CustomAdjacentObject then
                            return 1
                        end
                    end
                end
            end
        end
    end
    return 0
end
"""

# Anchor line that appears right after FROM_RINGS_WONDERS in the vanilla file.
SPECIFIC_WONDER_ANCHOR    = "    end\n--统计模块-> 环数内的国家公园"
SPECIFIC_WONDER_REPLACEMENT = "    end\n" + SPECIFIC_WONDER_FUNC + "\n--统计模块-> 环数内的国家公园"

# ---------------------------------------------------------------------------
# Vanilla anchor texts  (grabbed verbatim from the latest workshop version)
# ---------------------------------------------------------------------------

# 1. CallAdjacencyFunction block
VANILLA_CAF = r"""    function CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        -- 1. 获取函数
        local func = RuivoAdjacencyDispatch[AdjacencyType]

        --print(AdjacencyType, func)

        if not func then return -1 end
        --print("第一步过关")

        -- 2. 获取元数据
        local info = RuivoAdjacencyInfo[AdjacencyType]
        if not info then return -1 end
        --print("第二步过关")

        -- 3. 根据 AttributeType 传参
        local attr = info.AttributeType

        --全局游戏层级
        if attr == 'Game' then
            return func(CustomAdjacentObject) -- 部分函数可能不需要参数，Lua会自动忽略多余参数
        
        --单元格层级
        elseif attr == 'Plot' then
            return func(iX, iY, Rings, CustomAdjacentObject)

        --区域层级
        elseif attr == 'District' then
            return func(iX, iY, Rings, CustomAdjacentObject)

        --城市层级
        elseif attr == 'City' then
            return func(City, CustomAdjacentObject)
        
        --玩家层级
        elseif attr == 'Player' then
            return func(playerID, CustomAdjacentObject)
        
        --宗教层级
        elseif attr == 'Religion' then
            --可能的特殊处理
            if AdjacencyType == 'FROM_RELIGION_CITY_PLAYER_FOLLOWERS' then
                return func(playerID, iX, iY)
            else
                return func(playerID)
            end
        end

        --print("啊哦，看起来全部跳过了")

        return -1
    end
"""

PATCHED_CAF = r"""    function CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        -- 1. 获取函数
        -- CSC CUSTOM: handle FROM_RINGS_SPECIFIC_WONDER before dispatch (non-standard signature)
        if AdjacencyType == 'FROM_RINGS_SPECIFIC_WONDER' then
            return FROM_RINGS_SPECIFIC_WONDER(iX, iY, playerID, City, CustomAdjacentObject, iMinRings, iMaxRings)
        end
        local func = RuivoAdjacencyDispatch[AdjacencyType]

        --print(AdjacencyType, func)

        if not func then return -1 end
        --print("第一步过关")

        -- 2. 获取元数据
        local info = RuivoAdjacencyInfo[AdjacencyType]
        if not info then return -1 end
        --print("第二步过关")

        -- 3. 根据 AttributeType 传参
        local attr = info.AttributeType

        --全局游戏层级
        if attr == 'Game' then
            return func(CustomAdjacentObject) -- 部分函数可能不需要参数，Lua会自动忽略多余参数
        
        --单元格层级
        elseif attr == 'Plot' then
            return func(iX, iY, iMaxRings, CustomAdjacentObject)

        --区域层级
        elseif attr == 'District' then
            return func(iX, iY, iMaxRings, CustomAdjacentObject)

        --城市层级
        elseif attr == 'City' then
            return func(City, CustomAdjacentObject)
        
        --玩家层级
        elseif attr == 'Player' then
            return func(playerID, CustomAdjacentObject)
        
        --宗教层级
        elseif attr == 'Religion' then
            --可能的特殊处理
            if AdjacencyType == 'FROM_RELIGION_CITY_PLAYER_FOLLOWERS' then
                return func(playerID, iX, iY)
            else
                return func(playerID)
            end
        end

        --print("啊哦，看起来全部跳过了")

        return -1
    end
"""

# 2. StatsModule_For_GP
VANILLA_SMGP = r"""    function StatsModule_For_GP(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 Environment="GamePlay" 才执行
        if info and info.Environment == 'GamePlay' then
            --print("GP开始了",CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings))
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        end
        return -1
    end
"""

PATCHED_SMGP = r"""    function StatsModule_For_GP(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 Environment="GamePlay" 才执行
        if info and info.Environment == 'GamePlay' then
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        end
        return -1
    end
"""

# 3. StatsModule_For_UI
VANILLA_SMUI = r"""    function StatsModule_For_UI(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 Environment="UserInterface" 才执行
        if info and info.Environment == 'UserInterface' then
            --print("UI开始了",CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings))
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        end
        return -1
    end
"""

PATCHED_SMUI = r"""    function StatsModule_For_UI(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 Environment="UserInterface" 才执行
        if info and info.Environment == 'UserInterface' then
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        end
        return -1
    end
"""

# 4. StatsModule_For_Display
VANILLA_SMDP = r"""    function StatsModule_For_Display(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 CanDisplay=1 才执行
        if info and info.CanDisplay then
            --print("显示开始了",CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings))
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, Rings)
        end
        return -1
    end
"""

PATCHED_SMDP = r"""    function StatsModule_For_Display(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        local info = RuivoAdjacencyInfo[AdjacencyType]
        -- 只有配置了 CanDisplay=1 才执行
        if info and info.CanDisplay then
            return CallAdjacencyFunction(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, City, iMinRings, iMaxRings)
        end
        return -1
    end
"""

# 5. StatsModule_For_Display call site (already uses single Rings in vanilla)
VANILLA_SMDP_CALL = (
    "local iBonus = StatsModule_For_Display("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pkCity, row.Rings)"
)
PATCHED_SMDP_CALL = (
    "local iBonus = StatsModule_For_Display("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pkCity, row.MinRings, row.MaxRings)"
)

# 6-8. NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua -- three StatsModule_For_GP call sites
VANILLA_GP_CALL_1 = (
    "                                    local iBonus = StatsModule_For_GP("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.Rings)"
)
PATCHED_GP_CALL_1 = (
    "                                    local iBonus = StatsModule_For_GP("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.MinRings, row.MaxRings)"
)

VANILLA_GP_CALL_2 = (
    "                        local iBonus = StatsModule_For_GP("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.Rings)"
)
PATCHED_GP_CALL_2 = (
    "                        local iBonus = StatsModule_For_GP("
    "row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.MinRings, row.MaxRings)"
)

# Site 3: vanilla may already have MinRings/MaxRings (partial upstream patch).
# Try both the old un-patched form and the already-patched form.
VANILLA_GP_CALL_3_OLD = (
    "                                            local iBonus = "
    "StatsModule_For_GP(row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.Rings)"
)
VANILLA_GP_CALL_3_NEW = (
    "                                            local iBonus = "
    "StatsModule_For_GP(row.AdjacencyType, row.CustomAdjacentObject, "
    "iX, iY, playerID, pCity, row.MinRings, row.MaxRings)"
)
VANILLA_GP_CALL_3 = VANILLA_GP_CALL_3_OLD
PATCHED_GP_CALL_3 = VANILLA_GP_CALL_3_NEW

# ---------------------------------------------------------------------------
# Patch engine
# ---------------------------------------------------------------------------

def _apply(file_path: pathlib.Path, patches: list,
           extra_anchor=None, extra_replacement=None):
    text = file_path.read_text(encoding="utf-8")
    ok, changed = 0, 0

    for desc, old, new in patches:
        n = text.count(old)
        if n == 0:
            # For GP call site 3, the vanilla may already be patched.
            if desc.endswith("3 (OnDistrictCompleted)"): 
                # Check if already in target state
                already = text.count(new)
                if already > 0:
                    print(f"  [OK]   {desc}  (already has correct form)")
                    continue
                print(f"  [SKIP] {desc}  (neither old nor new form found)")
                continue
            print(f"  [SKIP] {desc}  (anchor text not found)")
            continue
        if extra_anchor and desc.startswith("Insert"):
            if extra_anchor not in text:
                print(f"  [SKIP] {desc}  (insertion anchor not found)")
                continue
            if extra_replacement.split("\n")[1] in text:
                print(f"  [SKIP] {desc}  (already present)")
                continue
        text = text.replace(old, new)
        changed += 1
        print(f"  [OK]   {desc}")

    if extra_anchor and not any(
        d.startswith("Insert") for d, _, _ in patches
    ):
        if extra_anchor in text and extra_replacement.split("\n")[1] not in text:
            text = text.replace(extra_anchor, extra_replacement)
            changed += 1
            print(f"  [OK]   FROM_RINGS_SPECIFIC_WONDER inserted")
        elif extra_replacement.split("\n")[1] in text:
            print(f"  [SKIP] FROM_RINGS_SPECIFIC_WONDER (already present)")
        else:
            print(f"  [SKIP] FROM_RINGS_SPECIFIC_WONDER (anchor not found)")

    if not DRY_RUN and changed:
        bak = file_path.with_suffix(file_path.suffix + ".prepatch_bak")
        if not bak.exists():
            shutil.copy2(file_path, bak)
            print(f"  [BACKUP] {bak.name}")
        file_path.write_text(text, encoding="utf-8")
        print(f"  [WRITTEN] {file_path.name}")
    elif DRY_RUN and changed:
        print(f"  [--dry-run] would write {file_path.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

print("=" * 60)
print("CSC MAB Patch Script")
print(f"Source dir : {SRC_DIR}")
print(f"DRY RUN    : {DRY_RUN}")
print("=" * 60)

stat_patches = [
    ("CallAdjacencyFunction", VANILLA_CAF, PATCHED_CAF),
    ("StatsModule_For_GP",   VANILLA_SMGP, PATCHED_SMGP),
    ("StatsModule_For_UI",   VANILLA_SMUI, PATCHED_SMUI),
    ("StatsModule_For_Display sig", VANILLA_SMDP, PATCHED_SMDP),
    ("StatsModule_For_Display site", VANILLA_SMDP_CALL, PATCHED_SMDP_CALL),
]

gp_patches = [
    ("GP call site 1 (Refresh_Core)",       VANILLA_GP_CALL_1, PATCHED_GP_CALL_1),
    ("GP call site 2 (Single_District)",    VANILLA_GP_CALL_2, PATCHED_GP_CALL_2),
    ("GP call site 3 (OnDistrictCompleted)", VANILLA_GP_CALL_3, PATCHED_GP_CALL_3),
]

print("\nRUIVO_STAT_MODULE_GP.lua")
_apply(STAT_FILE, stat_patches,
       extra_anchor=SPECIFIC_WONDER_ANCHOR,
       extra_replacement=SPECIFIC_WONDER_REPLACEMENT)

print("\nNEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua")
_apply(GP_FILE, gp_patches)

print("\nDone.")
if DRY_RUN:
    print("(no files were written -- remove --dry-run to apply)")
