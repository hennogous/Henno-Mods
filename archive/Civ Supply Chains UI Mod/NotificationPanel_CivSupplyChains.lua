-- ===========================================================================
-- CACHE BASE FUNCTIONS
-- ===========================================================================
print("NotificationPanel_CivSupplyChains script loaded!!!")
local BASE_RegisterHandlers = RegisterHandlers;

local NewBakersEffectNotifcation 	= DB.MakeHash("NOTIFICATION_CSC_BAKERS_EFFECT_NEW")
local IncreasedBakersEffectNotifcation = DB.MakeHash("NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED")
local DecreasedBakersEffectNotifcation = DB.MakeHash("NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED")
local RemovedBakersEffectNotifcation = DB.MakeHash("NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED")
-- ===========================================================================
function RegisterHandlers()
	BASE_RegisterHandlers();

	g_notificationHandlers[NewBakersEffectNotifcation]			= MakeDefaultHandlers();
	g_notificationHandlers[NewBakersEffectNotifcation].AddSound	= "ALERT_POSITIVE";
	--
	g_notificationHandlers[IncreasedBakersEffectNotifcation]			= MakeDefaultHandlers();
	g_notificationHandlers[IncreasedBakersEffectNotifcation].AddSound	= "ALERT_POSITIVE";

	g_notificationHandlers[DecreasedBakersEffectNotifcation]			= MakeDefaultHandlers();
	g_notificationHandlers[DecreasedBakersEffectNotifcation].AddSound	= "ALERT_NEGATIVE";
	
	g_notificationHandlers[RemovedBakersEffectNotifcation]			= MakeDefaultHandlers();
	g_notificationHandlers[RemovedBakersEffectNotifcation].AddSound	= "ALERT_NEGATIVE";
	-- Sounds
	----- ALERT_NEGATIVE
	----- ALERT_NEUTRAL
	----- ALERT_POSITIVE
	----- NOTIFICATION_MISC_POSITIVE
	----- NOTIFICATION_REBELLION
	----- UNIT_PROMOTION_AVAILABLE
	----- NOTIFICATION_OTHER_CIV_BUILD_WONDER
	----- NOTIFICATION_ESPIONAGE_OP_SUCCESS
	----- NOTIFICATION_ESPIONAGE_OP_FAILED
end

