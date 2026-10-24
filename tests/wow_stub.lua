-- Test double for the documented 3.3.5 surface; this is not a client emulator.
_clock = 0
_frames = {}
_cv = { Sound_MusicVolume = '0.35', Sound_EnableMusic = '0' }
_music = { played = 0, stopped = 0 }
_guid = '0xF1300000C5000001'
_text = 'Original English dialogue.'
_build = '12340'
_quests = {}
SlashCmdList = {}
local templates = { UIPanelButtonTemplate = true, UIPanelScrollFrameTemplate = true,
    InterfaceOptionsCheckButtonTemplate = true, OptionsSliderTemplate = true }
local function Widget(kind, name)
    local w = { kind = kind, name = name, scripts = {}, events = {}, shown = false, children = {} }
    function w:SetScript(event, fn) self.scripts[event] = fn end
    function w:RegisterEvent(event) self.events[event] = true end
    function w:GetName() return self.name end
    function w:Show() self.shown = true; self.explicitHidden = false; if self.scripts.OnShow then self.scripts.OnShow(self) end end
    function w:Hide() self.shown = false; self.explicitHidden = true end
    function w:IsShown() return self.shown end
    function w:SetText(text) self.text = text end
    function w:GetText() return self.text end
    function w:GetStringHeight() return 30 end
    function w:SetChecked(value) self.checked = value end
    function w:GetChecked() return self.checked end
    function w:SetValue(value) self.value = value; if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self, value) end end
    function w:SetBackdrop(value) self.backdrop = value end
    function w:GetBackdrop() return self.backdrop end
    function w:CreateFontString() local c = Widget('FontString'); c.parent = self; table.insert(self.children,c); return c end
    function w:CreateTexture() local c = Widget('Texture'); c.parent = self; table.insert(self.children,c); return c end
    function w:SetWidth(value) self.width = value end
    function w:GetWidth() return self.width or 1280 end
    function w:GetHeight() return self.height or 720 end
    function w:SetHeight(value) self.height = value end
    function w:SetAlpha(value) self.alpha = value end
    function w:GetAlpha() return self.alpha or 1 end
    function w:SetScale(value) self.scale = value end
    function w:SetTexture(value) self.texture = value end
    function w:SetFont(path, size, flags) self.font = {path, size, flags}; return true end
    function w:SetTextColor(...) self.textColor = {...} end
    function w:SetVertexColor(...) self.vertexColor = {...} end
    function w:SetPoint(...) self.points = self.points or {}; table.insert(self.points, {...}) end
    function w:ClearAllPoints() self.points = {} end
    function w:SetJustifyH(value) self.justifyH = value end
    function w:SetJustifyV(value) self.justifyV = value end
    function w:SetBackdropColor(...) self.color = {...} end
    function w:SetBackdropBorderColor(...) self.borderColor = {...} end
    function w:SetStatusBarTexture(value) assert(self.kind == 'StatusBar'); self.texture = value end
    function w:SetStatusBarColor(...) assert(self.kind == 'StatusBar'); self.barColor = {...} end
    if kind == 'PlayerModel' then
        function w:SetUnit(unit)
            if _modelError then error('model unavailable') end
            assert(UnitGUID(unit)); self.unit = unit
            self.model = _modelLoads ~= false and 'Creature\\Example\\Example.m2' or nil
        end
        function w:GetModel() return self.model end
        function w:ClearModel() self.model = nil; self.unit = nil end
        function w:SetSequence(value) self.sequence = value end
        function w:SetCamera(value) self.camera = value end
        function w:SetFacing(value) self.facing = value end
    end
    -- These are ordinary legacy frame/font/editbox methods. Do not absorb
    -- arbitrary unknown methods: a mistaken modern method should fail tests.
    for _, method in ipairs({ 'SetAllPoints', 'SetFrameStrata', 'EnableMouse',
        'SetMovable', 'RegisterForDrag', 'StartMoving', 'StopMovingOrSizing',
        'SetScrollChild', 'SetVerticalScroll', 'SetMinMaxValues', 'SetValueStep', 'SetMultiLine',
        'SetFontObject', 'SetAutoFocus', 'SetMaxLetters', 'SetFocus', 'HighlightText' }) do
        w[method] = function() end
    end
    return w
end
UIParent = Widget('Frame', 'UIParent')
ChatFontNormal = {}
function CreateFrame(kind, name, parent, template)
    if kind == 'PlayerModel' and _modelUnsupported then error('Unsupported PlayerModel') end
    if template then assert(templates[template], 'Non-legacy template: ' .. template) end
    local w = Widget(kind, name)
    w.parent = parent
    if parent and parent.children then table.insert(parent.children,w) end
    table.insert(_frames, w)
    if name then
        _G[name] = w
        for _, suffix in ipairs({ 'Text', 'Low', 'High' }) do _G[name .. suffix] = Widget('FontString') end
    end
    return w
end
DEFAULT_CHAT_FRAME = { AddMessage = function() end }
function UnitName(unit) if unit == 'player' then return 'Teste' else return 'NPC' end end
function UnitGUID() return _guid end
function UnitClass() return 'Warrior', 'WARRIOR' end
function UnitRace() return 'Orc', 'Orc' end
function UnitSex() return 2 end
function UnitAffectingCombat() return _combat or false end
function GetLocale() return 'enUS' end
function GetBuildInfo() return '3.3.5', _build, '', 30300 end
function GetTime() return _clock end
function GetCVar(key) return _cv[key] end
function SetCVar(key, value) _cv[key] = tostring(value) end
function PlayMusic(path) _music.played = _music.played + 1; _music.path = path end
function StopMusic() _music.stopped = _music.stopped + 1 end
function GetQuestText() return _text end
function GetProgressText() return _text end
function GetRewardText() return _text end
function GetGossipText() return _text end
function GetGreetingText() return _text end
function GetTitleText() return 'English title' end
function GetNumQuestLogEntries() return #_quests end
function GetQuestLogTitle(i)
    local q = _quests[i]
    if q then return q.title, 1, nil, nil, q.header, nil, nil, nil, q.id end
end
function InterfaceOptions_AddCategory() end
function InterfaceOptionsFrame_OpenToCategory() end
function QuestInfo_Display() end
function GossipFrameUpdate() end
function QuestFrameProgressPanel_OnShow() end
function QuestFrameGreetingPanel_OnShow() end
function hooksecurefunc(name, post)
    local original = _G[name]
    _G[name] = function(...) original(...); post(...) end
end
for _, name in ipairs({ 'GossipGreetingText', 'GreetingText', 'QuestProgressText',
    'QuestInfoDescriptionText', 'QuestInfoRewardText', 'QuestInfoObjectivesText', 'QuestInfoTitleHeader' }) do
    _G[name] = Widget('FontString', name)
end
QuestInfoFrame = {}
QuestFrame = Widget('Frame', 'QuestFrame')
GossipFrame = Widget('Frame', 'GossipFrame')
for name, text in pairs({ QuestInfoObjectivesHeader = 'Quest Objectives',
    QuestInfoDescriptionHeader = 'Description', QuestInfoRewardsHeader = 'Rewards',
    QuestInfoItemChooseText = 'You will be able to choose one of these rewards:',
    QuestInfoItemReceiveText = 'You will also receive:', QuestFrameAcceptButton = 'Accept',
    QuestFrameDeclineButton = 'Decline', QuestFrameCompleteQuestButton = 'Complete Quest',
    GossipFrameGreetingGoodbyeButton = 'Goodbye' }) do
    _G[name] = Widget('TextOrButton', name)
    _G[name]:SetText(text)
end
function Emit(event, ...)
    for _, f in ipairs(_frames) do if f.events[event] and f.scripts.OnEvent then f.scripts.OnEvent(f, event, ...) end end
end
function Tick(delta)
    _clock = _clock + delta
    for _, f in ipairs(_frames) do if f.scripts.OnUpdate then f.scripts.OnUpdate(f, delta) end end
end
