-- TAP_MC_MODE_REMOVE_PROJECTS
-- Author: Henno
-- Moved from Civ Supply Chains: T&P owns competing commissioning projects.
--------------------------------------------------------------

DELETE FROM Projects
WHERE ProjectType LIKE 'PROJECT_CREATE_CORPORATION_PRODUCT_%';
