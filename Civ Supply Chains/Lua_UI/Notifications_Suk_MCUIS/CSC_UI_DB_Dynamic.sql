--==========================================================================================================================
-- Zegangani: 
--==========================================================================================================================

--===========================================================================================================================================================================--
/*	CITY ABILITY MODIFIERS */
--===========================================================================================================================================================================--

-- Step 1: Fill AbilityEffectModifierId from ModifierArguments.Value
UPDATE CSC_AbilityAttachModifiers
SET AbilityEffectModifierId = (
    SELECT b.Value
    FROM ModifierArguments b
    WHERE b.ModifierId = CSC_AbilityAttachModifiers.ModifierId
);

-- Step 2: Fill ArgumentAmount based on linked relationship in ModifierArguments
UPDATE CSC_AbilityAttachModifiers
SET AbilityArgumentAmount = (
    SELECT b2.Value
    FROM ModifierArguments b1
    JOIN ModifierArguments b2 ON b1.Value = b2.ModifierId
    WHERE b1.ModifierId = CSC_AbilityAttachModifiers.ModifierId
		AND b2.Name = 'Amount'
);

-- Step 3: Fill ModifierDesc from ModifierStrings.Text
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



