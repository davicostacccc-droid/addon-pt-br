import sys
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from read_lua_data import literal, numeric_rows
from prepare_kalimdor_beta import acceptable, convert, source_supported
from build_kalimdor_beta import safe_lua, narration


class BetaImportTests(unittest.TestCase):
    def test_literal_reader_preserves_nested_values_and_escapes(self):
        self.assertEqual(literal(r'''{[7]={[14]={{1.2,3}}},nil,"A\nB",['x']='it\'s'}'''),
                         {7:{14:{1:{1:1.2,2:3}}},1:None,2:'A\nB','x':"it's"})
        for text in ('os.execute("bad")','{[1]=function() end}','{}; error("bad")'):
            with self.assertRaises(ValueError): literal(text)

    def test_duplicate_database_ids_are_rejected(self):
        with self.assertRaises(ValueError): list(numeric_rows('[1]={},\n[1]={},'))

    def test_wrong_quest_quantities_and_english_are_rejected(self):
        self.assertEqual(acceptable('Leve dez caudas.', 'Bring eight tails.'),'number_difference')
        self.assertEqual(acceptable('You will bring the tails to your leader.', 'Bring tails.'),'likely_english')
        self.assertIsNone(acceptable('Mate 8 inimigos.', 'Kill 8 enemies.'))
        self.assertFalse(source_supported('Bring $s1 items.'))

    def test_beta_markers_are_resolved_without_executing_code(self):
        text=convert('YOUR_NAME, voc\u00ea est\u00e1 vivYOUR_GENDER(o;a).NEW_LINEYOUR_CLASS')
        self.assertEqual(text,'$n, voc\u00ea est\u00e1 viv$go:a;.\n$c')
        self.assertEqual(narration(text),'aventureiro, voc\u00ea est\u00e1 vivo.\naventureiro')
        lua=LuaRuntime()
        content='Ol\u00e1 "}; error("bad") --\n\\\t'
        self.assertEqual(lua.eval(safe_lua(content)),content)


if __name__=='__main__': unittest.main()
