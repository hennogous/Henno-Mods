--==========================================================================================================================
-- Zegangani: Making Sure that Rings (MaxRings) in table 'Ruivo_New_Adjacency' is never lower than MinRings
--==========================================================================================================================
UPDATE Ruivo_New_Adjacency SET Rings = MinRings WHERE MinRings > Rings;
