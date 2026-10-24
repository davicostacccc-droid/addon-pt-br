import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_pack as pack


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_catalog_and_unsafe_markers(self):
        self.assertEqual(len(pack.load_catalog(ROOT / 'data' / 'demo.json')['lines']), 3)
        row = {'event': 'QUEST_DETAIL', 'npc': 197, 'source': 'source', 'translation': 'Olá, $n!'}
        pack.validate_row(row)
        self.assertEqual(pack.spoken_text(row), 'Olá, aventureiro!')
        for bad in ['Olá, $c', '|cFFFF00texto', '[[ phonemes ]]']:
            with self.assertRaises(ValueError):
                pack.validate_row(dict(row, translation=bad))
        with self.assertRaises(ValueError):
            pack.validate_row(dict(row, review_required=True))

    def test_lua_string_is_inert_even_with_executable_content(self):
        value = '"}); os.execute("evil"); -- Olá\n\\'
        lua = LuaRuntime()
        self.assertEqual(lua.eval(pack.lua_string(value)), value)

    def test_cache_validates_bytes_and_fingerprint(self):
        audio, meta = self.path / 'sound.mp3', self.path / 'sound.json'
        audio.write_bytes(b'example')
        meta.write_text(json.dumps({'fingerprint': 'a', 'duration': 1.5, 'sha256': pack.digest(audio)}))
        self.assertIsNotNone(pack.valid_cache(audio, meta, 'a'))
        self.assertIsNone(pack.valid_cache(audio, meta, 'changed-model'))
        audio.write_bytes(b'corrupted')
        self.assertIsNone(pack.valid_cache(audio, meta, 'a'))

    def test_build_emits_loadable_pack_without_execution(self):
        model = self.path / 'test.onnx'; model.write_bytes(b'test-model')
        Path(str(model) + '.json').write_text('{}')
        audio = self.path / 'fake.mp3'; audio.write_bytes(b'test-mp3')
        out = self.path / 'release' / 'AzerothVoz'
        with patch.object(pack, 'generate', return_value=(audio, 2.0, False)):
            result = pack.build(ROOT / 'data' / 'demo.json', model, out, self.path / 'cache')
        self.assertEqual(result['lines'], 3)
        lua = LuaRuntime()
        lua.execute((ROOT / 'addon' / 'AzerothVoz' / 'Core.lua').read_text(encoding='utf-8'))
        lua.execute((out / 'Pack.lua').read_text(encoding='utf-8'))
        self.assertIsNotNone(lua.eval("AzerothVoz.Lookup('DEMO',0,'Welcome to Azeroth.')"))
        with self.assertRaises(FileExistsError):
            pack.build(ROOT / 'data' / 'demo.json', model, out, self.path / 'cache')

    def test_import_roundtrip_and_refuse_overwrite(self):
        src, out = self.path / 'capture.json', self.path / 'queue.json'
        src.write_text(json.dumps({'version': 1, 'lines': [{'event': 'QUEST_COMPLETE', 'npc': 197,
            'source': 'Hi, $n!', 'title': 'English title', 'unknown_path': 'ignored'}]}), encoding='utf-8')
        command = [sys.executable, str(ROOT / 'tools' / 'import_captures.py'), str(src), '--out', str(out)]
        subprocess.run(command, check=True, capture_output=True)
        line = json.loads(out.read_text(encoding='utf-8'))['lines'][0]
        self.assertEqual(line['translation'], '')
        self.assertNotIn('unknown_path', line)
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_invalid_event_and_npc_rejected(self):
        for npc in [True, -1, '197', 0x1000000]:
            with self.assertRaises(ValueError):
                pack.validate_row({'event': 'GOSSIP_SHOW', 'npc': npc, 'source': 'x', 'translation': 'y'})
        with self.assertRaises(ValueError):
            pack.validate_row({'event': 'C_GossipInfo', 'npc': 197, 'source': 'x', 'translation': 'y'})


if __name__ == '__main__':
    unittest.main()
