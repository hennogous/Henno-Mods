"""Formatting must preserve executable SQL, comments and literal text."""

import importlib.util
import sqlite3
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "layout_under_test", Path(__file__).resolve().parents[1] / "format_sql_layout.py"
)
LAYOUT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAYOUT)


class SqlLayoutTests(unittest.TestCase):
    def check_format(self, sql):
        formatted = LAYOUT.format_sql_layout_text(sql)
        self.assertEqual(LAYOUT.sql_tokens(sql), LAYOUT.sql_tokens(formatted))
        self.assertEqual(formatted, LAYOUT.format_sql_layout_text(formatted))
        return formatted

    def compare_execution(self, sql):
        formatted = self.check_format(sql)
        dumps = []
        for script in (sql, formatted):
            with sqlite3.connect(":memory:") as db:
                db.executescript(script)
                # SQLite stores trigger source verbatim in sqlite_master.
                dumps.append([LAYOUT.sql_tokens(line) for line in db.iterdump()])
        self.assertEqual(dumps[0], dumps[1])
        return formatted

    def test_inline_headers_values_and_column_alignment(self):
        formatted = self.compare_execution(
            "CREATE TABLE t(a,b);\nINSERT INTO t(a,b) VALUES('a','x'),('long','y');\n"
        )
        lines = formatted.splitlines()
        self.assertEqual(lines[-2].index("'x'"), lines[-1].index("'y'"))

    def test_seven_columns_and_nested_expressions(self):
        formatted = self.compare_execution(
            "CREATE TABLE t(a,b,c,d,e,f,g);\n"
            "INSERT INTO t(a,b,c,d,e,f,g) VALUES(1,2,3,4,5,6,coalesce(NULL,7));\n"
        )
        self.assertIn("\n        coalesce(NULL,7)\n", formatted)
        self.assertIn("\n        a,\n        b,", formatted)

    def test_wide_select_case_subquery_and_union(self):
        formatted = self.compare_execution(
            "CREATE TABLE t(a,b,c,d,e,f,g);\n"
            "INSERT INTO t(a,b,c,d,e,f,g) SELECT DISTINCT 1,2,3,4,"
            "CASE WHEN 1 THEN 'FROM' ELSE 'WHERE' END,(SELECT max(5,6)),7 "
            "UNION ALL SELECT 8,9,10,11,12,13,14;\n"
        )
        self.assertIn("SELECT\n        8,\n        9,", formatted)

    def test_quoted_keywords_and_identifiers(self):
        self.compare_execution(
            'CREATE TABLE "INSERT"("VALUES", [SELECT]);\n'
            'INSERT INTO "INSERT"("VALUES",[SELECT]) VALUES(\'INSERT\',\'a, b\');\n'
        )

    def test_multiline_literals_escaped_quotes_and_comment_markers(self):
        self.compare_execution(
            "CREATE TABLE t(a,b);\nINSERT INTO t(a,b) VALUES"
            "('first  line\nsecond\tline  ', 'it''s -- /* text */');\n"
        )

    def test_comments_and_commented_out_sql_survive(self):
        sql = (
            "/* INSERT INTO fake(a,b,c,d,e,f,g) VALUES(1,2,3,4,5,6,7); */\n"
            "CREATE TABLE t(a,b);\nINSERT INTO t(a,b) VALUES\n"
            "-- group A\n(1, /* keep */ 2), -- row note\n(3,4);\n"
        )
        formatted = self.compare_execution(sql)
        self.assertTrue(formatted.startswith(sql.splitlines()[0]))

    def test_column_labels_align_values_without_rewriting_comments(self):
        formatted = self.compare_execution(
            "CREATE TABLE t(a,b);\nINSERT INTO t(a,b) VALUES\n"
            "(/* a, */ 1, /* LongerLabel */ 2);\n"
        )
        lines = formatted.splitlines()
        values = [line for line in lines if '/*' in line]
        self.assertEqual(values[0].index('1'), values[1].index('2'))

    def test_legacy_tab_inside_column_comment(self):
        formatted = self.compare_execution(
            "CREATE TABLE t(a,b); INSERT INTO t(a,b) VALUES"
            "(/*\tShort */ 1, /* LongerLabel */ 2);\n"
        )
        values = [line.expandtabs(4) for line in formatted.splitlines() if '/*' in line]
        self.assertEqual(values[0].index('1'), values[1].index('2'))

    def test_upsert_trigger_and_insert_without_columns(self):
        self.compare_execution(
            "CREATE TABLE t(a PRIMARY KEY,b); CREATE TABLE log(a,b);\n"
            "CREATE TRIGGER record AFTER INSERT ON t BEGIN "
            "INSERT INTO log(a,b) VALUES(NEW.a,NEW.b); END;\n"
            "INSERT INTO t(a,b) VALUES(1,2) ON CONFLICT(a) DO UPDATE SET b=excluded.b;\n"
            "INSERT INTO t VALUES(2,3);\n"
        )

    def test_operator_boundaries_do_not_change(self):
        self.compare_execution(
            "CREATE TABLE t(a,b); INSERT INTO t(a,b) VALUES(1 - -2,'a'||'b');\n"
        )


if __name__ == "__main__":
    unittest.main()
