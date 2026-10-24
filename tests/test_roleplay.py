from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class RoleplayTests(unittest.TestCase):
    def setup_ui(self, before=''):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT/'tests/wow_stub.lua').read_text(encoding='utf-8'))
        self.lua.execute(before)
        for name in ('Core.lua','Pack.lua','Theme.lua','UI.lua','Roleplay.lua','Events.lua'):
            self.lua.execute((ROOT/'addon/AzerothVoz'/name).read_text(encoding='utf-8'))
        self.lua.execute("Emit('ADDON_LOADED','AzerothVoz')")
        self.lua.execute("""
            local a=AzerothVoz
            a.Register({event='QUEST_DETAIL',npc=197,questID=10,source='English dialogue.',translation='Olá, aventureiro!',title='Missão',audio='audio\\\\test.mp3',duration=10})
            _text='English dialogue.'; QuestFrame:Show()
        """)

    def run_lua(self, code): self.lua.execute(code)

    def test_live_model_fade_talk_progress_and_stop(self):
        self.setup_ui()
        self.run_lua("""
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            local a=AzerothVoz; local f=a.roleplay
            assert(f:IsShown() and f.shade:IsShown())
            assert(not a.reader:IsShown() and not a.controls:IsShown())
            assert(f.modelReady and f.model.unit=='questnpc' and f.model.sequence==60)
            assert(f.speakerName:GetText()=='NPC' and f.text:GetText()=='Olá, aventureiro!')
            Tick(0.3); assert(f:GetAlpha()==1)
            Tick(2); assert(f.progress.value>0 and f.progress.value<1)
            SlashCmdList.AZEROTHVOZ('parar')
            assert(not a.playing and f.model.sequence==0 and f:IsShown())
            SlashCmdList.AZEROTHVOZ('repetir'); assert(a.playing and f.model.sequence==60)
            Tick(11); assert(not a.playing and f.progress.value==1 and f.model.sequence==0)
            Emit('QUEST_FINISHED'); assert(not f:IsShown() and not f.shade:IsShown() and not a.playing)
        """)

    def test_minimize_and_mode_switch_preserve_native_actions(self):
        self.setup_ui()
        self.run_lua("""
            local clicked=false
            QuestFrameAcceptButton:SetScript('OnClick',function() clicked=true end)
            Emit('QUEST_DETAIL'); Tick(0.1)
            local a=AzerothVoz
            a.roleplay.minimizeButton.scripts.OnClick()
            assert(not a.roleplay:IsShown() and a.controls:IsShown() and a.playing)
            QuestFrameAcceptButton.scripts.OnClick(); assert(clicked)
            SlashCmdList.AZEROTHVOZ('rp on'); assert(a.roleplay:IsShown())
            SlashCmdList.AZEROTHVOZ('rp off'); assert(not a.roleplay:IsShown() and a.controls:IsShown())
            assert(a.playing)
        """)

    def test_missing_changed_or_failed_model_keeps_reading(self):
        for before in ('_modelUnsupported=true','_modelError=true','_modelLoads=false'):
            with self.subTest(before=before):
                self.setup_ui(before)
                self.run_lua("""
                    Emit('QUEST_DETAIL'); Tick(0.1); Tick(1.2)
                    local f=AzerothVoz.roleplay
                    assert(f:IsShown() and f.fallback:IsShown() and not f.modelReady)
                    assert(AzerothVoz.playing)
                """)
        self.setup_ui()
        self.run_lua("""
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            assert(AzerothVoz.roleplay.modelReady)
            _guid='0xF1300000C6000001'; Tick(0.1)
            assert(not AzerothVoz.roleplay.modelReady and AzerothVoz.roleplay.fallback:IsShown())
        """)

    def test_preview_never_uses_unrelated_unit_and_model_toggle_works(self):
        self.setup_ui()
        self.run_lua("""
            SlashCmdList.AZEROTHVOZ('previa 10'); Tick(0.2)
            assert(AzerothVoz.roleplay:IsShown() and not AzerothVoz.roleplay.modelReady)
            assert(AzerothVoz.roleplay.fallback:IsShown())
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            assert(AzerothVoz.roleplay.modelReady)
            SlashCmdList.AZEROTHVOZ('modelo off')
            assert(not AzerothVoz.roleplay.modelReady and AzerothVoz.roleplay.fallback:IsShown())
        """)

    def test_combat_logout_missing_text_and_disabling_cleanup(self):
        for stop in ("Emit('PLAYER_REGEN_DISABLED')","Emit('PLAYER_LOGOUT')","SlashCmdList.AZEROTHVOZ('off')"):
            with self.subTest(stop=stop):
                self.setup_ui()
                self.run_lua("Emit('QUEST_DETAIL'); Tick(0.1); "+stop)
                self.run_lua("assert(not AzerothVoz.roleplay:IsShown() and not AzerothVoz.roleplay.shade:IsShown() and not AzerothVoz.playing)")
        self.setup_ui('_combat=true')
        self.run_lua("Emit('QUEST_DETAIL'); Tick(0.1); assert(not AzerothVoz.roleplay:IsShown())")
        self.setup_ui()
        self.run_lua("Emit('QUEST_DETAIL'); Tick(0.1); _text='Unknown'; Emit('QUEST_DETAIL'); Tick(0.1); assert(not AzerothVoz.roleplay:IsShown() and AzerothVoz.reader:IsShown())")

    def test_same_entry_new_spawn_rebinds_speaker_without_wrong_portrait(self):
        self.setup_ui()
        self.run_lua("""
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            local before=AzerothVoz.current
            _guid='0xF1300000C5000002'
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            assert(AzerothVoz.current~=before)
            assert(AzerothVoz.current.speaker.guid==_guid and AzerothVoz.roleplay.modelReady)
        """)

    def test_pages_preserve_utf8_and_every_character(self):
        self.setup_ui()
        paginate = self.lua.eval('AzerothVoz.RoleplayPages')
        for text in ('', 'Olá, campeão!\n\n' * 80, 'á' * 700, 'a ' + 'é' * 756, 'Uma história com ação e emoção. ' * 60):
            pages = paginate(text)
            values = [pages[i] for i in range(1, len(pages) + 1)]
            self.assertEqual(''.join(values), text)
            self.assertTrue(all(len(page) <= 250 for page in values))

    def test_auto_pages_manual_reading_objectives_and_replay(self):
        self.setup_ui()
        self.lua.globals()._long = ('Uma história com ação e emoção. ' * 70)
        self.run_lua("""
            local a=AzerothVoz
            a.quests[10].QUEST_DETAIL.translation=_long
            a.quests[10].QUEST_DETAIL.objectives='Encontre 8 aliados.'
            Emit('QUEST_DETAIL'); Tick(0.1); Tick(0.1)
            local f=a.roleplay
            assert(#f.pages>2 and f.page==1)
            Tick(4); assert(f.page>1)
            f.previousButton.scripts.OnClick(); local manual=f.page
            Tick(2); assert(f.manualPage and f.page==manual)
            f.autoButton.scripts.OnClick(); Tick(0.1); assert(not f.manualPage and f.page>=manual)
            f.objectivesButton.scripts.OnClick(); assert(f.inObjectives and f.text:GetText()=='Encontre 8 aliados.')
            f.autoButton.scripts.OnClick(); Tick(0.1); assert(not f.inObjectives and not f.manualPage)
            f.repeatButton.scripts.OnClick(); assert(f.page==1 and not f.manualPage)
            Tick(11); assert(f.page==#f.pages and f.progress.value==1)
        """)

    def test_scene_scale_compensates_ui_scale_and_reset_centers(self):
        self.setup_ui()
        self.run_lua("""
            UIParent:SetWidth(1920); UIParent:SetHeight(1080); AzerothVoz.CenterRoleplay()
            local normal=AzerothVoz.roleplay.scale
            UIParent:SetWidth(2560); UIParent:SetHeight(1440); AzerothVoz.CenterRoleplay()
            assert(math.abs(AzerothVoz.roleplay.scale*0.75-normal)<0.001)
            AzerothVoz.roleplay:SetPoint('LEFT',0,0)
            SlashCmdList.AZEROTHVOZ('centralizar')
            assert(#AzerothVoz.roleplay.points==1 and AzerothVoz.roleplay.points[1][1]=='CENTER')
        """)

    def test_modern_settings_toggles_control_voice_and_mode(self):
        self.setup_ui()
        self.run_lua("""
            Emit('QUEST_DETAIL'); Tick(0.1)
            AzerothVoz_voice.scripts.OnClick(AzerothVoz_voice)
            assert(not AzerothVoz.db.voice and not AzerothVoz.playing)
            AzerothVoz_roleplay.scripts.OnClick(AzerothVoz_roleplay)
            assert(not AzerothVoz.db.roleplay and not AzerothVoz.roleplay:IsShown())
        """)

    def test_settings_open_outside_small_legacy_options_container(self):
        self.setup_ui()
        self.run_lua("""
            assert(not AzerothVoz.settings:IsShown())
            SlashCmdList.AZEROTHVOZ('')
            assert(AzerothVoz.settings:IsShown() and AzerothVoz.options~=AzerothVoz.settings)
            assert(AzerothVoz.settings.height==590 and AzerothVoz.settings.width==550)
            assert(AzerothVoz.settings.scale>0)
        """)


if __name__=='__main__': unittest.main()
