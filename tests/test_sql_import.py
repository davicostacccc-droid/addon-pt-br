import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from import_quest_locale_sql import read_rows, audit


class SqlImportTests(unittest.TestCase):
    def test_implicit_columns_and_numeric_literals(self):
        text = 'CREATE TABLE `example` (\n  `id` int,\n  `factor` float,\n  `text` text\n) ENGINE=InnoDB;\nINSERT INTO `example` VALUES (1,0.5,\'hello\'),(2,1e-3,NULL);'
        rows = list(read_rows(text, 'example'))
        self.assertEqual(rows, [{'id': 1, 'factor': 0.5, 'text': 'hello'}, {'id': 2, 'factor': 0.001, 'text': None}])

    def test_literals_preserve_commas_markers_and_quotes(self):
        text = r"INSERT INTO `quest_template_locale` (`ID`,`locale`,`Title`,`Details`,`VerifiedBuild`) VALUES (4641,'ptBR','O seu lugar','Olá, $N! D\'água; $B$BOrcs, trolls.',47168),(7,'ptBR','Outra','uma ''citação''',47168);"
        rows = list(read_rows(text))
        self.assertEqual(rows[0]['Details'], "Olá, $N! D'água; $B$BOrcs, trolls.")
        self.assertEqual(rows[1]['Details'], "uma 'citação'")

    def test_reject_executable_expressions(self):
        text = "INSERT INTO `quest_template_locale` (`ID`) VALUES (LOAD_FILE('/private'));"
        with self.assertRaises(ValueError):
            list(read_rows(text))

    def test_audit_flags_other_build_and_has_no_gossip(self):
        text = "INSERT INTO `quest_template_locale` (`ID`,`locale`,`Title`,`Details`,`VerifiedBuild`) VALUES (7,'ptBR','Título','Return to McBride',47168),(8,'enUS','Ignored',NULL,12340);"
        index, report = audit(text)
        self.assertEqual(list(index['quests']), ['7'])
        self.assertEqual(report['source_builds'], {'47168': 1})
        self.assertEqual(report['possible_english_fields_heuristic'], {'Details': 1})
        self.assertFalse(report['playable'])
        self.assertEqual(report['gossip_records'], 0)

    def test_duplicate_id_is_not_silently_overwritten(self):
        with self.assertRaises(ValueError):
            audit("INSERT INTO `quest_template_locale` (`ID`,`locale`) VALUES (7,'ptBR'),(7,'ptBR');")
