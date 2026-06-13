-- TAP_PRODUCT_SUBSTRATE
-- Parked Specialty Products substrate moved out of Civ Supply Chains.
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Shared specialty product great work object and slot
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Test B spike: use Firaxis' vanilla Product object/slot identity even when the
-- Monopolies & Corporations game mode is not active. Product handling in the UI
-- and DLL is hard-coded to GREATWORKOBJECT_PRODUCT / GREATWORKSLOT_PRODUCT;
-- custom CSC Product-like object/slot rows could be created by CE but crashed on
-- next-turn processing. These INSERT OR IGNORE rows are a minimal compatibility
-- shim and defer to M&C's native rows whenever that mode has already loaded them.
INSERT OR IGNORE INTO Types

		(	Type,								Kind				)
VALUES	(	'PSEUDOYIELD_GREATWORK_PRODUCT',	'KIND_PSEUDOYIELD'	);

INSERT OR IGNORE INTO PseudoYields

		(	PseudoYieldType,					DefaultValue	)
VALUES	(	'PSEUDOYIELD_GREATWORK_PRODUCT',	10.0			);

INSERT OR IGNORE INTO GreatWorkObjectTypes

		(	GreatWorkObjectType,			Value,	PseudoYieldType,				Name,							IconString				)
VALUES	(	'GREATWORKOBJECT_PRODUCT',	9,		'PSEUDOYIELD_GREATWORK_PRODUCT',	'LOC_GREATWORKOBJECT_PRODUCT',	'[ICON_GreatWork_Product]'	);

INSERT OR IGNORE INTO GreatWorkSlotTypes

		(	GreatWorkSlotType		)
VALUES	(	'GREATWORKSLOT_PRODUCT'	);

INSERT OR IGNORE INTO GreatWork_ValidSubTypes

		(	GreatWorkSlotType,			GreatWorkObjectType		)
VALUES	(	'GREATWORKSLOT_PRODUCT',	'GREATWORKOBJECT_PRODUCT'	);

