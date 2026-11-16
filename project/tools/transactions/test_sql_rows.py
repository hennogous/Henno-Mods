"""Mixed native SQL migrations preserve unrelated effects and comments."""
import sqlite3
import unittest
from sql_rows import remove_rows


class SqlRows(unittest.TestCase):
    def test_mixed_values_removes_only_selected_rows_with_embedded_commas_and_comments(self):
        source="""CREATE TABLE A(ModifierId,Value);
INSERT INTO A(ModifierId,Value) VALUES
-- before
('keep','comma, and ''quote'''),
/* middle */ ('move',2),
('keep2',(1+3)),
-- final
('move2',5);
"""
        changed,count=remove_rows(source,'A','ModifierId',{'move','move2'})
        db=sqlite3.connect(':memory:');db.executescript(changed)
        self.assertEqual(db.execute('SELECT * FROM A').fetchall(),[('keep',"comma, and 'quote'"),('keep2',4)])
        self.assertEqual(count,2)
        for comment in ['-- before','/* middle */','-- final']:self.assertIn(comment,changed)

    def test_select_filters_output_column_and_rejects_mixed_dynamic_output(self):
        source="INSERT INTO A(Owner,ModifierId) SELECT 'move','keep' WHERE 1;"
        self.assertEqual(remove_rows(source,'A','ModifierId',{'move'}),(source,0))
        source="INSERT INTO A(Owner,ModifierId) SELECT Owner,'move' FROM Owners;"
        self.assertEqual(remove_rows(source,'A','ModifierId',{'move'})[1],1)
        source="INSERT INTO A(Owner,ModifierId) SELECT Owner,CASE WHEN Owner=1 THEN 'move' ELSE 'keep' END FROM Owners;"
        with self.assertRaisesRegex(AssertionError,'mixed/dynamic'):remove_rows(source,'A','ModifierId',{'move'})

    def test_whole_insert_preserves_its_comments(self):
        changed,n=remove_rows("INSERT INTO A(ModifierId,Value) VALUES ('move',/* reason */1);",'A','ModifierId',{'move'})
        self.assertEqual(n,1);self.assertEqual(changed,'/* reason */')


if __name__=='__main__':unittest.main()
