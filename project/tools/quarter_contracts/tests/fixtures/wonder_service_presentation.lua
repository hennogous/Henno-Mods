-- UI boundary fixture: four logical venue anchors. GameEffects reports one
-- modifier instance per producer and one district subject for its venue.
local template={
    ModifierId='MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',
    AbilityEffectModifierId='MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',
    AbilityArgumentAmount=2,
    AbilityIcon='ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE',
    AbilityIconTarget='BUILDING_CSC_TAILORS_STAGE_4_SERVICE',
    AbilityDesc='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION',
    AbilityNewDesc='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_NEW',
    AbilityIncreasedDesc='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_INCREASED',
    AbilityDecreasedDesc='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_DECREASED',
    AbilityRemovedDesc='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_REMOVED',
    NotificationQuarter='TAILORS',
};
local venues={'CUSTOMER','BOLSHOI','BROADWAY','SYDNEY'};
local anchors={};
for _,venue in ipairs(venues)do
    local suffix=venue=='CUSTOMER' and '' or '_'..venue;
    local row={};for k,v in pairs(template)do row[k]=v;end;
    row.ModifierId='MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_'..venue;
    row.AbilityEffectModifierId=template.AbilityEffectModifierId..suffix;
    row.AbilityIcon=template.AbilityIcon..suffix;
    for _,key in ipairs({'AbilityDesc','AbilityNewDesc','AbilityIncreasedDesc','AbilityDecreasedDesc','AbilityRemovedDesc'})do
        local state=key=='AbilityDesc' and '' or '_'..({AbilityNewDesc='NEW',AbilityIncreasedDesc='INCREASED',AbilityDecreasedDesc='DECREASED',AbilityRemovedDesc='REMOVED'})[key];
        row[key]='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'..suffix..state;
    end;
    table.insert(anchors,row);
end;
GameInfo.CSC_AbilityAttachModifiers=function()
    local index=0;return function()index=index+1;return anchors[index];end;
end;
presentationSellers={{City=seller,Venues={CUSTOMER=true,BOLSHOI=true,BROADWAY=true,SYDNEY=true}}};
local function subjects(id)
    local source=presentationSellers[math.floor((id-1)/4)+1];
    local venue=venues[(id-1)%4+1];
    if not source.Venues[venue] or not hasOpera or (source.City:GetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED') or 0)<=0 then return {};end;
    if venue=='CUSTOMER' or customer:GetProperty('CSC_TAILORS_STAGE_4_SERVICE_'..venue..'_READY')==1 then return {venue};end;
    return {};
end;
GameEffects={
    GetModifiers=function()local result={};for i=1,#presentationSellers*4 do result[i]=i;end;return result;end,
    GetModifierDefinition=function(id)return {Id=anchors[(id-1)%4+1].ModifierId};end,
    GetModifierActive=function(id)return #subjects(id)>0;end,
    GetModifierSubjectCount=function(id)return #subjects(id);end,
    GetModifierSubjects=subjects,
    GetObjectType=function()return 'District';end,
    GetObjectString=function(subject)
        return 'District: 42, Owner: '..customer:GetOwner()..', SubType: 1, SubValue: -1, City: '..customer:GetID();
    end,
};
local function event()return {Add=function()end,Remove=function()end};end;
LuaEvents=setmetatable({},{__index=function(self,key)local value=event();self[key]=value;return value;end});
Events=setmetatable(Events,{__index=function(self,key)local value=event();self[key]=value;return value;end});
include=function()end;
Game={GetLocalPlayer=function()return 0;end};
DB={MakeHash=function(value)return value;end};
ParameterTypes={MESSAGE='message',SUMMARY='summary',LOCATION='location'};
notifications={};abilityCache={};
ReadCustomData=function(key)return abilityCache[key];end;
WriteCustomData=function(key,value)abilityCache[key]=value;end;
NotificationManager={SendNotification=function(player,kind,data)
    table.insert(notifications,{player=player,kind=kind,data=data});
end};
Locale.Lookup=function(key,...)
    local result=tostring(key);for _,value in ipairs({...})do result=result..'|'..tostring(value);end;return result;
end;
UI.GetHeadSelectedCity=function()return customer;end;
registeredIcons={};
registration={RegisterCityIcon=function(_,name)table.insert(registeredIcons,name);end};
icon={SetIconData=function(self,make,request,description,image)
    self.make=make;self.description=description;self.image=image;
end};
