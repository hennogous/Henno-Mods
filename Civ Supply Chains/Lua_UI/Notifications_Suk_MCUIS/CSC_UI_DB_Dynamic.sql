--==========================================================================================================================
-- Zegangani: 
--==========================================================================================================================

--===========================================================================================================================================================================--
/*	CITY ABILITY MODIFIERS */
--===========================================================================================================================================================================--

-- CSC_AbilityAttachModifiers is seeded with attach modifier IDs in gameplay SQL.
-- This late UI database pass resolves those attach modifiers into the inner
-- effect modifier, amount, and preview text that CSC_UI_Notifications.lua needs
-- when comparing current city effects against the saved notification cache.

-- Step 1: follow the attach modifier's ModifierId argument to find the inner effect modifier.
UPDATE CSC_AbilityAttachModifiers
SET AbilityEffectModifierId = (
    SELECT b.Value
    FROM ModifierArguments b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.ModifierId
);

-- Step 2: read the inner effect modifier's Amount argument. The notification
-- script multiplies this by stack-count changes to produce signed delta text.
UPDATE CSC_AbilityAttachModifiers
SET AbilityArgumentAmount = (
    SELECT b2.Value
    FROM ModifierArguments b1
    JOIN ModifierArguments b2 ON b1.Value = b2.ModifierId
    WHERE b1.ModifierId = CSC_AbilityAttachModifiers.ModifierId
		AND b2.Name = 'Amount'
);

-- Step 3: read the inner effect modifier's Preview string. Suffix variants are
-- localization keys for new/increased/decreased/removed notification wording.
UPDATE CSC_AbilityAttachModifiers
SET AbilityDesc = (
    SELECT b.Text
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.AbilityEffectModifierId
		AND b.Context = 'Preview'
);

-- New
UPDATE CSC_AbilityAttachModifiers
SET AbilityNewDesc = (
    SELECT b.Text || '_NEW'
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.AbilityEffectModifierId
      AND b.Context = 'Preview'
);

-- Increased
UPDATE CSC_AbilityAttachModifiers
SET AbilityIncreasedDesc = (
    SELECT b.Text || '_INCREASED'
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.AbilityEffectModifierId
      AND b.Context = 'Preview'
);

-- Decreased
UPDATE CSC_AbilityAttachModifiers
SET AbilityDecreasedDesc = (
    SELECT b.Text || '_DECREASED'
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.AbilityEffectModifierId
      AND b.Context = 'Preview'
);

-- Removed
UPDATE CSC_AbilityAttachModifiers
SET AbilityRemovedDesc = (
    SELECT b.Text || '_REMOVED'
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.AbilityEffectModifierId
      AND b.Context = 'Preview'
);

--===========================================================================================================================================================================--
/*	CITY SPECIALIST MODIFIERS */
--===========================================================================================================================================================================--
/*
-- Step 1: Fill SpecialistGrantModifierId from ModifierArguments.Value
UPDATE CSC_SpecialistAttachModifiers
SET SpecialistGrantModifierId = (
    SELECT b.Value
    FROM ModifierArguments b
    WHERE b.ModifierId = CSC_SpecialistAttachModifiers.ModifierId
);

-- Step 2: Fill SpecialistGrantDesc from ModifierStrings.Text
UPDATE CSC_SpecialistAttachModifiers
SET SpecialistGrantDesc = (
    SELECT b.Text
    FROM ModifierStrings b
    WHERE b.ModifierId = CSC_SpecialistAttachModifiers.SpecialistGrantModifierId
		AND b.Context = 'Preview'
); */


