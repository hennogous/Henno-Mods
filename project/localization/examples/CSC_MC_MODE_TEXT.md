# CSC_MC_MODE_TEXT Example
output: project/localization/examples/generated/CSC_MC_MODE_TEXT.sql
language: en_US

This example is intentionally not loaded by ModBuddy. It demonstrates the
Markdown source format for long `LocalizedText` rows and `UPDATE` overrides.

## LOC_CSC_EXAMPLE_MARKDOWN_ONLY
mode: upsert

This short row demonstrates INSERT OR REPLACE generation. It is only written to the example output file.

## Bakers Stage 2 M&C Override
mode: update
tags: LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION, LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION

- +1 [ICON_Food] Food from each adjacent Base Materials improvement, increased to +2 [ICON_Food] Food from an Industry and +3 [ICON_Food] Food from a Corporation, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold, increased to +2 each for an Industry and +3 each for a Corporation.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from the local Bakery and Café, in exchange for +1 [ICON_Food] Food.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from an adjacent Granary, in exchange for +1 [ICON_Food] Food.
- +1 [ICON_Food] Food bonus to [ICON_TradeRoute] Trade Routes to the city, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Quarter, if the origin city does not have a Bakers' Quarter.

At Feudalism, a supplied Water Mill or Wind Mill can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service in an adjacent City Center with a Granary.

## LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION
mode: update

- +1 [ICON_Food] Food from each adjacent Specialty Materials improvement, increased to +2 [ICON_Food] Food from an Industry and +3 [ICON_Food] Food from a Corporation, in exchange for +1 [ICON_Production] Production, increased to +2 [ICON_Production] Production to an Industry and +3 [ICON_Production] Production to a Corporation.
- +1 [ICON_Citizen] Citizen slot, +1 [ICON_Food] Food and +1 [ICON_Culture] Culture to [ICON_Citizen] Citizens in the Quarter.
- +1 [ICON_Food] Food from the local Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Culture] Culture to each adjacent Zoo and Ferris Wheel for every 5 [ICON_Citizen] Citizens in the city, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Café for every 5 [ICON_Citizen] Citizens in each adjacent Zoo or Ferris Wheel city.
- +1 [ICON_Food] Food bonus to [ICON_TradeRoute] Trade Routes to the city, in exchange for +1 [ICON_Production] Production and +2 [ICON_Gold] Gold to the Quarter, if the origin city does not have a Bakers' Quarter.

At Urbanization, a supplied Café can establish services in adjacent Entertainment Complexes with Zoos and Water Parks with Ferris Wheels.

## LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN
mode: update

- +1 [ICON_Food] Food from each adjacent Specialty Materials improvement, increased to +2 [ICON_Food] Food from an Industry and +3 [ICON_Food] Food from a Corporation, in exchange for +1 [ICON_Production] Production, increased to +2 [ICON_Production] Production to an Industry and +3 [ICON_Production] Production to a Corporation.
- +1 [ICON_Citizen] Citizen slot, +1 [ICON_Food] Food and +1 [ICON_Culture] Culture to [ICON_Citizen] Citizens in the Quarter.
- +1 [ICON_Food] Food from the local Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Culture] Culture to each adjacent Zoo, Ferris Wheel, and Conservatory for every 5 [ICON_Citizen] Citizens in the city, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Café for every 5 [ICON_Citizen] Citizens in each adjacent Zoo, Ferris Wheel, or Conservatory city.
- +1 [ICON_Food] Food bonus to [ICON_TradeRoute] Trade Routes to the city, in exchange for +1 [ICON_Production] Production and +2 [ICON_Gold] Gold to the Quarter, if the origin city does not have a Bakers' Quarter.

At Urbanization, a supplied Café can establish services in adjacent Entertainment Complexes with Zoos, Water Parks with Ferris Wheels, and Gardens with Conservatories.
