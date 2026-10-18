-- Execute the shipped notification handler against live and serialized caches.
function include() end
function print() end
DB = {MakeHash=function(value)
    local result=0; for i=1,#value do result=(result*31+string.byte(value,i))%2147483647; end
    return result;
end};
Locale={Lookup=function(value,...) return value; end};
local effect='TEST_EFFECT';
GameInfo={CSC_AbilityAttachModifiers=function()
    local done=false;
    return function()
        if done then return nil; end; done=true;
        return {ModifierId='TEST_ATTACH',AbilityEffectModifierId=effect,AbilityArgumentAmount=2,
            AbilityDesc='Desc',AbilityNewDesc='New',AbilityIncreasedDesc='Increased',
            AbilityDecreasedDesc='Decreased',AbilityRemovedDesc='Removed',NotificationQuarter='TEST'};
    end;
end};
Events=setmetatable({}, {__index=function() return {Add=function() end}; end});
Game={GetLocalPlayer=function() return 0; end};
ParameterTypes={MESSAGE=1,SUMMARY=2,LOCATION=3};
local cache=nil;
function ReadCustomData() return cache; end
function WriteCustomData(key,value) cache=value; end
local sent={};
NotificationManager={SendNotification=function(player,kind,data) table.insert(sent,kind); end};
local count=2;
local city={GetID=function() return 7; end,GetX=function() return 1; end,GetY=function() return 2; end,GetName=function() return 'Test'; end};
Players={[0]={GetCities=function() return {Members=function()
    local done=false;return function() if done then return nil; end;done=true;return 1,city;end;
end};end}};
GameEffects={
    GetModifiers=function() return {1}; end,
    GetModifierDefinition=function() return {Id='TEST_ATTACH'}; end,
    GetModifierActive=function() return count>0; end,
    GetModifierSubjectCount=function() return count; end,
    GetModifierSubjects=function() local values={};for i=1,count do values[i]=i;end;return values;end,
    GetObjectType=function() return 'District'; end,
    GetObjectString=function() return 'District: 1, Owner: 0, City: 7'; end,
};
local function serialize(value)
    if type(value)~='table' then return value; end
    local result={};for key,child in pairs(value) do result[type(key)=='string' and DB.MakeHash(key) or key]=serialize(child);end
    return result;
end
function TestNotificationCache()
    OnRefreshCityQuarters();assert(#sent==1,'first ability should notify once');
    cache=serialize(cache);OnRefreshCityQuarters();assert(#sent==1,'reload must not emit a false removal/new notification');
    count=3;OnRefreshCityQuarters();assert(#sent==2 and sent[2]==DB.MakeHash('NOTIFICATION_CSC_TEST_EFFECT_INCREASED'),'loaded cache must preserve increase comparison');
    cache=serialize(cache);count=1;OnRefreshCityQuarters();assert(#sent==3 and sent[3]==DB.MakeHash('NOTIFICATION_CSC_TEST_EFFECT_DECREASED'),'loaded cache must preserve decrease comparison');
    cache=serialize(cache);count=0;OnRefreshCityQuarters();assert(#sent==4 and sent[4]==DB.MakeHash('NOTIFICATION_CSC_TEST_EFFECT_REMOVED'),'loaded cache must preserve removal comparison');
    cache={[7]={[DB.MakeHash('RETIRED_EFFECT')]={[DB.MakeHash('StackAmount')]=2}}};
    OnRefreshCityQuarters();assert(#sent==4,'unknown historical effect must not crash or create a bogus removal');
end
