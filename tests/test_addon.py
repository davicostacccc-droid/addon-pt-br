import json
from pathlib import Path
import sys
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_pack import key, lua_string, normalize, text_hash


class AddonTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT / 'tests' / 'wow_stub.lua').read_text(encoding='utf-8'))
        self.lua.execute('AzerothVozDB = { roleplay = false }')
        for name in ('Core.lua', 'Pack.lua', 'Theme.lua', 'UI.lua', 'Roleplay.lua', 'Events.lua'):
            self.lua.execute((ROOT / 'addon' / 'AzerothVoz' / name).read_text(encoding='utf-8'))
        self.lua.execute("Emit('ADDON_LOADED', 'AzerothVoz')")

    def run_lua(self, source):
        self.lua.execute(source)

    def register(self, event='GOSSIP_SHOW', text='Original English dialogue.'):
        row = {'event': event, 'npc': 197, 'source': text, 'translation': 'Olá, aventureiro!',
               'title': 'Título', 'audio': 'audio\\sample.mp3', 'duration': 3.5}
        literal = ','.join(f'{k}={v if isinstance(v, (float, int)) else lua_string(v)}' for k, v in row.items())
        self.run_lua('AzerothVoz.Register({' + literal + '})')

    def test_lua51_and_python_normalization_hash_agree(self):
        self.assertEqual(self.lua.eval('_VERSION'), 'Lua 5.1')
        for value in [' Hello\r\nWORLD\t', 'Olá, $n! AÇÃO', '"\\\n', 'Árvore', 'a\u00a0b']:
            self.assertEqual(self.lua.eval('AzerothVoz.Normalize')(value), normalize(value))
            self.assertEqual(self.lua.eval('AzerothVoz.Hash')(normalize(value)), text_hash(normalize(value)))

    def test_old_guid_only(self):
        self.run_lua("""
            assert(AzerothVoz.NpcID('0xF1300000C5000001') == 197)
            assert(AzerothVoz.NpcID('0xF150000337000001') == 823)
            assert(AzerothVoz.NpcID('0x0000000000000001') == nil)
            assert(AzerothVoz.NpcID('Creature-0-1-2-3-197-0') == nil)
            assert(AzerothVoz.NpcID(nil) == nil)
        """)

    def test_source_markers_resolve_but_do_not_allow_other_text(self):
        self.register('QUEST_DETAIL', 'Hello, $N!$B$BYou are a $c of the $r people.')
        self.run_lua(r"""
            assert(AzerothVoz.Lookup('QUEST_DETAIL',197,'Hello, Teste!\n\nYou are a warrior of the orc people.'))
            assert(not AzerothVoz.Lookup('QUEST_DETAIL',197,'Hello, Other! You are a warrior of the orc people.'))
            assert(not AzerothVoz.Lookup('QUEST_DETAIL',198,'Hello, Teste! You are a warrior of the orc people.'))
            assert(not AzerothVoz.Lookup('QUEST_DETAIL',197,'Hello, Teste! You are a mage of the orc people.'))
        """)

    def test_source_gender_marker(self):
        self.register('QUEST_DETAIL', 'Welcome, $gson:daughter; of the Horde.')
        self.run_lua("""
            assert(AzerothVoz.Lookup('QUEST_DETAIL',197,'Welcome, son of the Horde.'))
            UnitSex = function() return 3 end
            assert(AzerothVoz.Lookup('QUEST_DETAIL',197,'Welcome, daughter of the Horde.'))
            assert(not AzerothVoz.Lookup('QUEST_DETAIL',197,'Welcome, son of the Horde.'))
        """)

    def test_name_tokenization_respects_utf8_and_word_boundaries(self):
        self.run_lua("""
            UnitName = function() return 'José' end
            assert(AzerothVoz.Tokenize('Olá, José!') == 'Olá, $n!')
            assert(AzerothVoz.Tokenize('José e José.') == '$n e $n.')
            assert(AzerothVoz.Tokenize('Josézinho') == 'Josézinho')
            UnitName = function() return 'It' end
            assert(AzerothVoz.Tokenize('It is with It.') == '$n is with $n.')
        """)

    def test_exact_match_and_no_fuzzy(self):
        self.register()
        self.run_lua("""
            assert(AzerothVoz.Lookup('GOSSIP_SHOW',197,' ORIGINAL English dialogue. '))
            assert(not AzerothVoz.Lookup('GOSSIP_SHOW',197,'Original English dialogue!'))
            assert(not AzerothVoz.Lookup('GOSSIP_SHOW',198,'Original English dialogue.'))
            assert(not AzerothVoz.Lookup('QUEST_COMPLETE',197,'Original English dialogue.'))
        """)

    def test_hash_collision_still_checks_text(self):
        self.run_lua("AzerothVoz.Hash = function() return '1' end")
        self.register()
        self.run_lua("assert(not AzerothVoz.Lookup('GOSSIP_SHOW',197,'Wrong speech.'))")

    def test_play_and_restore_after_duration(self):
        self.register()
        self.run_lua("""
            Emit('GOSSIP_SHOW'); Tick(0.1)
            assert(_music.played == 1)
            assert(_cv.Sound_EnableMusic == '1' and _cv.Sound_MusicVolume == '0.7')
            Tick(5)
            assert(_music.stopped == 1)
            assert(_cv.Sound_EnableMusic == '0' and _cv.Sound_MusicVolume == '0.35')
            assert(AzerothVoz.db.musicBefore == nil)
        """)

    def test_duplicate_event_does_not_restart(self):
        self.register()
        self.run_lua("Emit('GOSSIP_SHOW'); Tick(0.1); Emit('GOSSIP_SHOW'); Tick(0.1); assert(_music.played == 1)")

    def test_close_cancels_pending_and_reopen_can_play(self):
        self.register()
        self.run_lua("""
            Emit('GOSSIP_SHOW'); Emit('GOSSIP_CLOSED'); Tick(0.1)
            assert(_music.played == 0)
            Emit('GOSSIP_SHOW'); Tick(0.1); Emit('GOSSIP_CLOSED')
            assert(not AzerothVoz.reader:IsShown() and not AzerothVoz.playing)
            Emit('GOSSIP_SHOW'); Tick(0.1); assert(_music.played == 2)
        """)

    def test_late_gossip_close_does_not_cancel_quest(self):
        self.register('QUEST_DETAIL')
        self.run_lua("Emit('QUEST_DETAIL'); Emit('GOSSIP_CLOSED'); Tick(0.1); assert(_music.played == 1)")

    def test_unknown_line_stops_previous_and_captures(self):
        self.register()
        self.run_lua("""
            Emit('GOSSIP_SHOW'); Tick(0.1)
            _text = 'Unknown, Teste!'; Emit('GOSSIP_SHOW'); Tick(0.1)
            assert(_music.played == 1 and not AzerothVoz.playing)
            assert(AzerothVoz.count == 1)
        """)
        result = json.loads(self.lua.eval('AzerothVoz.ExportJSON()'))
        self.assertEqual(result['lines'][0]['source'], 'Unknown, $n!')

    def test_export_escapes_json_and_preserves_utf8(self):
        value = '"Olá"\\texto\n\t\x01'
        self.lua.eval('AzerothVoz.Capture')('QUEST_COMPLETE', 197, value, 'Título', 783)
        result = json.loads(self.lua.eval('AzerothVoz.ExportJSON()'))
        self.assertEqual(result['lines'][0]['source'], value)
        self.assertEqual(result['lines'][0]['questID'], 783)
        self.run_lua('AzerothVoz.Export(); assert(AzerothVoz.exportFrame:IsShown())')

    def test_capture_limit_and_hash_collisions(self):
        self.run_lua("""
            AzerothVoz.Hash = function() return '1' end
            AzerothVoz.Capture('GOSSIP_SHOW',197,'a','')
            AzerothVoz.Capture('GOSSIP_SHOW',197,'b','')
            assert(AzerothVoz.count == 2)
            AzerothVoz.count = 1000
            AzerothVoz.Capture('GOSSIP_SHOW',197,'c','')
            assert(AzerothVoz.count == 1000)
        """)
        self.assertEqual(len(json.loads(self.lua.eval('AzerothVoz.ExportJSON()'))['lines']), 2)

    def test_voice_toggle_still_translates(self):
        self.register()
        self.run_lua("""
            AzerothVoz.db.voice = false; Emit('GOSSIP_SHOW'); Tick(0.1)
            assert(_music.played == 0)
            assert(GossipGreetingText:GetText() == 'Olá, aventureiro!')
        """)

    def test_single_native_window_and_compact_controls(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            QuestFrame:Show(); Emit('QUEST_DETAIL'); Tick(0.1)
            assert(not AzerothVoz.reader:IsShown())
            assert(AzerothVoz.controls:IsShown())
            assert(QuestInfoObjectivesHeader:GetText() == 'Objetivos')
            assert(QuestInfoRewardsHeader:GetText() == 'Recompensas')
            assert(QuestFrameAcceptButton:GetText() == 'Aceitar')
            SlashCmdList.AZEROTHVOZ('repetir'); assert(_music.played == 2)
        """)

    def test_extra_window_option_and_fallback(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            QuestFrame:Show(); Emit('QUEST_DETAIL'); Tick(0.1)
            SlashCmdList.AZEROTHVOZ('janela on')
            assert(AzerothVoz.reader:IsShown() and not AzerothVoz.controls:IsShown())
            SlashCmdList.AZEROTHVOZ('janela off')
            assert(not AzerothVoz.reader:IsShown() and AzerothVoz.controls:IsShown())
            Emit('QUEST_FINISHED'); QuestFrame:Hide()
            Emit('QUEST_DETAIL'); Tick(0.1)
            assert(AzerothVoz.reader:IsShown())
            assert(not AzerothVoz.controls:IsShown() and AzerothVoz.nativeFrame == nil)
        """)

    def test_native_disappearance_stops_voice_and_hides_controls(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            QuestFrame:Show(); Emit('QUEST_DETAIL'); Tick(0.1)
            QuestFrame:Hide(); Tick(0.1)
            assert(not AzerothVoz.playing and not AzerothVoz.controls:IsShown())
            assert(not AzerothVoz.reader:IsShown() and AzerothVoz.current == nil)
            assert(_cv.Sound_MusicVolume == '0.35')
        """)

    def test_preview_keeps_reader_even_with_native_frame_open(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            local r = AzerothVoz.Lookup('QUEST_DETAIL',197,'Original English dialogue.')
            AzerothVoz.quests[788] = { QUEST_DETAIL = r }
            QuestFrame:Show(); Emit('QUEST_DETAIL'); Tick(0.1)
            SlashCmdList.AZEROTHVOZ('previa')
            assert(AzerothVoz.reader:IsShown() and not AzerothVoz.controls:IsShown())
            assert(AzerothVoz.nativeFrame == nil)
        """)

    def test_restore_native_preserves_newer_addon_updates_and_button_actions(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            QuestInfoDescriptionText:SetText('Original body')
            local callback = function() _accepted = true end
            QuestFrameAcceptButton:SetScript('OnClick', callback)
            QuestFrame:Show(); Emit('QUEST_DETAIL'); Tick(0.1)
            assert(QuestFrameAcceptButton.scripts.OnClick == callback)
            QuestInfoRewardsHeader:SetText('A newer label from another addon')
            SlashCmdList.AZEROTHVOZ('off')
            assert(QuestInfoObjectivesHeader:GetText() == 'Quest Objectives')
            assert(QuestFrameAcceptButton:GetText() == 'Accept')
            assert(QuestInfoDescriptionText:GetText() == 'Original body')
            assert(QuestInfoRewardsHeader:GetText() == 'A newer label from another addon')
            assert(not AzerothVoz.controls:IsShown())
        """)

    def test_unknown_gossip_keeps_reader_and_does_not_translate_labels(self):
        self.run_lua("""
            GossipFrame:Show(); Emit('GOSSIP_SHOW'); Tick(0.1)
            assert(AzerothVoz.reader:IsShown() and not AzerothVoz.controls:IsShown())
            assert(GossipFrameGreetingGoodbyeButton:GetText() == 'Goodbye')
        """)

    def test_native_quest_log_is_not_overwritten(self):
        self.register('QUEST_DETAIL')
        self.run_lua("""
            Emit('QUEST_DETAIL'); Tick(0.1)
            assert(QuestInfoDescriptionText:GetText() == 'Olá, aventureiro!')
            QuestInfoFrame.questLog = true
            QuestInfoDescriptionText:SetText('Other selected quest')
            QuestInfo_Display()
            assert(QuestInfoDescriptionText:GetText() == 'Other selected quest')
        """)

    def test_quest_metadata_id_is_not_title_guess(self):
        self.run_lua("""
            _quests = { {title='English title',id=783}, {title='English title',id=999} }
            Emit('QUEST_DETAIL'); Tick(0.1)
        """)
        self.assertNotIn('questID', json.loads(self.lua.eval('AzerothVoz.ExportJSON()'))['lines'][0])

    def test_missing_npc_clears_stale_voice(self):
        self.register()
        self.run_lua("""
            Emit('GOSSIP_SHOW'); Tick(0.1)
            _guid = nil; Emit('QUEST_DETAIL'); Tick(0.1)
            assert(not AzerothVoz.playing and AzerothVoz.current == nil)
        """)

    def test_off_and_logout_restore_settings(self):
        self.register()
        self.run_lua("""
            Emit('GOSSIP_SHOW'); Tick(0.1); SlashCmdList.AZEROTHVOZ('off')
            assert(_cv.Sound_MusicVolume == '0.35' and not AzerothVoz.db.enabled)
            SlashCmdList.AZEROTHVOZ('on'); Emit('GOSSIP_SHOW'); Tick(0.1)
            Emit('PLAYER_LOGOUT'); assert(_cv.Sound_MusicVolume == '0.35')
        """)

    def test_crash_snapshot_recovers(self):
        self.run_lua("""
            AzerothVozDB.musicBefore = { volume = '0.4', enabled = '1' }
            AzerothVoz.Init()
            assert(_cv.Sound_MusicVolume == '0.4' and AzerothVozDB.musicBefore == nil)
        """)

    def test_beta_shared_text_requires_unambiguous_title(self):
        self.run_lua("""
            local a = AzerothVoz
            a.Register({event='QUEST_PROGRESS',npc=197,questID=1,source='Do you have it?',sourceTitle='First',translation='Primeira'})
            a.Register({event='QUEST_PROGRESS',npc=197,questID=2,source='Do you have it?',sourceTitle='Second',translation='Segunda'})
            assert(not a.Lookup('QUEST_PROGRESS',197,'Do you have it?'))
            assert(a.Lookup('QUEST_PROGRESS',197,'Do you have it?','Second').questID == 2)
            assert(not a.Lookup('QUEST_PROGRESS',197,'Do you have it?','Other'))
        """)

    def test_beta_unbound_quest_only_matches_exact_source(self):
        self.run_lua("""
            local a = AzerothVoz
            a.Register({event='QUEST_DETAIL',npc=0,questID=3,source='An item starts this task.',sourceTitle='Item quest',translation='Uma missão de item'})
            a.Handle('QUEST_DETAIL',nil,'An item starts this task.','Item quest')
            assert(a.current and a.current.record.questID == 3)
            a.Handle('QUEST_DETAIL',nil,'Another task.','Item quest')
            assert(not a.current)
            assert(not a.Lookup('QUEST_DETAIL',197,'An item starts this task.','Item quest'))
        """)

    def test_beta_resolved_cache_updates_player_context_and_new_records(self):
        self.run_lua(r"""
            local a = AzerothVoz
            a.Register({event='QUEST_DETAIL',npc=197,questID=4,source='Hello $N.$B$c',translation='Olá'})
            assert(a.Lookup('QUEST_DETAIL',197,'Hello Teste.\nWarrior').questID == 4)
            local previous = a.resolved['QUEST_DETAIL:197']
            assert(a.Lookup('QUEST_DETAIL',197,'Hello Teste.\nWarrior'))
            assert(previous == a.resolved['QUEST_DETAIL:197'])
            local old = UnitName
            UnitName = function(u) if u == 'player' then return 'Nova' else return old(u) end end
            assert(a.Lookup('QUEST_DETAIL',197,'Hello Nova.\nWarrior'))
            assert(not a.Lookup('QUEST_DETAIL',197,'Hello Teste.\nWarrior'))
            a.Register({event='QUEST_DETAIL',npc=197,questID=5,source='Bye $N.',translation='Até logo'})
            assert(a.Lookup('QUEST_DETAIL',197,'Bye Nova.').questID == 5)
            assert(a.Expand('$n, $c $r.') == 'Nova, guerreiro orc.')
            UnitSex = function() return 3 end
            assert(a.Expand('viv$go:a;') == 'viva')
        """)

    def test_wrong_build_does_not_enable_events(self):
        self.run_lua("""
            _build = '99999'
            for _, f in ipairs(_frames) do f.events.GOSSIP_SHOW = nil end
            Emit('ADDON_LOADED','AzerothVoz')
            for _, f in ipairs(_frames) do assert(not f.events.GOSSIP_SHOW) end
        """)


if __name__ == '__main__':
    unittest.main()
