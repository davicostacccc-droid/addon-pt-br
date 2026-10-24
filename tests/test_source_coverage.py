import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from analyze_source_coverage import audio_phases, literal_ids, summarize


class SourceCoverageTests(unittest.TestCase):
    def test_index_does_not_treat_other_audio_or_phase_as_quest_narration(self):
        paths = ['pack/generated/sounds/quests/789-accept.mp3', 'pack/generated/sounds/quests/789-accept.mp3',
                 'pack/generated/sounds/quests/789-complete.mp3', 'pack/generated/sounds/gossip/123-accept.mp3',
                 'pack/generated/sounds/quests/790-invalid.mp3']
        self.assertEqual(audio_phases([{'path': p} for p in paths]), {789: {'accept', 'complete'}})

    def test_empty_details_and_id_overlap_do_not_count_as_translation(self):
        report = summarize({1: {}, 2: {}, 3: {}}, {'1': {'Details': '  '}, '2': {'Details': 'texto'},
                           '4': {'Details': 'texto'}}, {1, 2, 4}, {2, 5}, {2: {'accept'}, 4: {'accept', 'progress', 'complete'}})
        self.assertEqual(report['english_with_locale_details_and_questie_id'], 1)
        self.assertEqual(report['also_has_any_indexed_audio'], 1)
        self.assertEqual(report['also_has_all_three_audio_phases'], 0)
        self.assertEqual(report['questie_ptbr_overlap'], 1)

    def test_lua_is_read_as_text_without_executing_it(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'db.lua'
            path.write_text('error("do not run")\n[789] = {"test"},\n[789] = {},\n-- [7] = {},\n', encoding='utf-8')
            self.assertEqual(literal_ids(path), {789})


if __name__ == '__main__': unittest.main()
