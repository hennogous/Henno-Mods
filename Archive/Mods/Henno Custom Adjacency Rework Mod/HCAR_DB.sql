--==========================================================================================================================
-- Zegangani: adding new 'MinRings' Column to table 'Ruivo_New_Adjacency'
--==========================================================================================================================
ALTER TABLE Ruivo_New_Adjacency ADD COLUMN MinRings INTEGER NOT NULL DEFAULT 1;
