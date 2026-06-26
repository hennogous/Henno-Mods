# ModSupport_LGD_MC_MODE_TEXT
output: Civ Supply Chains/ModSupport/ModSupport_LGD_MC_MODE_TEXT.sql
language: en_US

M&C wording that must load after Leugi's Garden compatibility text.

## LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN
mode: update

- +1 [ICON_Food] Food from each adjacent [ICON_CSC_SPEC] Specialty Materials improvement, increased to +2 [ICON_Food] Food from an Industry and +3 [ICON_Food] Food from a Corporation, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold, increased to +2 each for an Industry and +3 each for a Corporation.
- +1 [ICON_Citizen] Citizen slot, +1 [ICON_Food] Food and +1 [ICON_Culture] Culture to [ICON_Citizen] Citizens in the Quarter.
- +1 [ICON_Food] Food from the local Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Culture] Culture to each adjacent Zoo, Ferris Wheel, and Conservatory for every 5 [ICON_Citizen] Citizens in the city, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Café for every 5 [ICON_Citizen] Citizens in each adjacent Zoo, Ferris Wheel, or Conservatory city.
- +1 [ICON_Food] Food bonus to [ICON_TradeRoute] Trade Routes to the city, in exchange for +1 [ICON_Production] Production and +2 [ICON_Gold] Gold to the Quarter, if the origin city does not have a Bakers' Quarter.

At Urbanization, a supplied Café can establish services in adjacent Entertainment Complexes with Zoos, Water Parks with Ferris Wheels, and Gardens with Conservatories.
