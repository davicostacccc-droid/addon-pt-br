local A = AzerothVoz
local frame = CreateFrame('Frame')
frame:RegisterEvent('ADDON_LOADED')

local functions = { QUEST_DETAIL = GetQuestText, QUEST_PROGRESS = GetProgressText,
    QUEST_COMPLETE = GetRewardText, GOSSIP_SHOW = GetGossipText, QUEST_GREETING = GetGreetingText }

local function Close()
    A.pending, A.current = nil, nil
    A.Stop()
    if A.reader then A.reader:Hide() end
    if A.controls then A.controls:Hide() end
    A.nativeFrame = nil
    A.RestoreNative()
end
A.Close = Close

local function QuestID(title)
    local found
    for i = 1, GetNumQuestLogEntries() do
        local name, _, _, _, header, _, _, _, id = GetQuestLogTitle(i)
        if not header and name == title then
            if found then return nil end
            found = id
        end
    end
    return found
end

local function RenderNative()
    local current = A.current
    local r = current and current.record
    if not r then return end
    local event = current.event
    local target
    if event == 'GOSSIP_SHOW' then target = GossipGreetingText
    elseif event == 'QUEST_GREETING' then target = GreetingText
    elseif event == 'QUEST_PROGRESS' then target = QuestProgressText
    elseif not (QuestInfoFrame and QuestInfoFrame.questLog) then
        if event == 'QUEST_DETAIL' then target = QuestInfoDescriptionText
        elseif event == 'QUEST_COMPLETE' then target = QuestInfoRewardText end
    end
    -- The separate reader always provides a scrollable fallback. We do not
    -- replace gossip buttons or alter quest actions/reward choices.
    local applied = target and A.NativeText(target, A.Expand(r.translation))
    if event == 'QUEST_DETAIL' and not (QuestInfoFrame and QuestInfoFrame.questLog) then
        if r.objectives then A.NativeText(QuestInfoObjectivesText, A.Expand(r.objectives)) end
        if r.title then A.NativeText(QuestInfoTitleHeader, r.title) end
    end
    local root = event == 'GOSSIP_SHOW' and GossipFrame or QuestFrame
    if applied then A.TranslateLabels(event) end
    A.UpdatePresentation(applied and root or nil)
end

frame:SetScript('OnEvent', function(self, event, name)
    if event == 'ADDON_LOADED' then
        if name ~= 'AzerothVoz' then return end
        A.Init()
        local _, build = GetBuildInfo()
        if tostring(build) ~= '12340' then
            A.Message('Cliente incompatível: esta versão exige build 12340.'); return
        end
        A.CreateUI()
        for ev in pairs(functions) do self:RegisterEvent(ev) end
        self:RegisterEvent('QUEST_FINISHED'); self:RegisterEvent('GOSSIP_CLOSED')
        self:RegisterEvent('PLAYER_LOGOUT')
        SLASH_AZEROTHVOZ1 = '/avoz'
        SlashCmdList.AZEROTHVOZ = function(input)
            input = string.lower(input or '')
            if input == 'demo' then
                Close(); A.Handle('DEMO', 0, 'Welcome to Azeroth.', 'Demonstração')
            elseif input:match('^previa%s*%d*$') then
                A.Preview(tonumber(input:match('%d+')) or 788)
            elseif input == 'parar' then A.Stop()
            elseif input == 'repetir' then A.Play(A.current and A.current.record)
            elseif input == 'janela on' or input == 'janela off' then
                A.db.extraWindow = input == 'janela on'
                if A.current then A.UpdatePresentation(A.nativeFrame) end
            elseif input == 'exportar' then A.Export()
            elseif input == 'cobertura' then
                A.Message(A.packInfo or 'Consulte o LEIA-ME do pacote para conhecer sua cobertura.')
            elseif input == 'off' then A.db.enabled = false; Close()
            elseif input == 'on' then A.db.enabled = true
            else InterfaceOptionsFrame_OpenToCategory(A.options) end
        end
        A.Message('Versão ' .. A.version .. ' carregada. /avoz demo ou /avoz para configurar.')
    elseif event == 'PLAYER_LOGOUT' then Close()
    elseif event == 'QUEST_FINISHED' or event == 'GOSSIP_CLOSED' then
        -- A late close event from the previous window must not erase the new
        -- window's pending line (gossip -> quest is a frequent transition).
        local kind = A.pending and A.pending.event or (A.current and A.current.event)
        if (event == 'GOSSIP_CLOSED' and kind == 'GOSSIP_SHOW') or
            (event == 'QUEST_FINISHED' and kind and kind ~= 'GOSSIP_SHOW' and kind ~= 'DEMO') then Close() end
    elseif functions[event] then
        local unit = event == 'GOSSIP_SHOW' and 'npc' or 'questnpc'
        local npc = A.NpcID(UnitGUID(unit))
        local text = functions[event]()
        local title = event == 'GOSSIP_SHOW' and UnitName(unit) or GetTitleText()
        -- Delay only presentation so Blizzard has finished updating its frames.
        A.pending = { event = event, npc = npc, text = text, title = title,
            questID = event ~= 'GOSSIP_SHOW' and QuestID(title) or nil, at = GetTime() + 0.05 }
    end
end)

frame:SetScript('OnUpdate', function()
    if A.pending and GetTime() >= A.pending.at then
        local p = A.pending; A.pending = nil
        A.Handle(p.event, p.npc, p.text, p.title, p.questID)
        RenderNative()
    end
    if A.endsAt and GetTime() >= A.endsAt then A.Stop() end
    if A.nativeFrame and not A.nativeFrame:IsShown() then Close() end
end)

-- UI can redraw without another dialogue event. Secure post-hooks retain
-- Blizzard's original functions. Rendering does not touch quest-log text.
for _, name in ipairs({ 'QuestInfo_Display', 'GossipFrameUpdate',
    'QuestFrameProgressPanel_OnShow', 'QuestFrameGreetingPanel_OnShow' }) do
    if type(_G[name]) == 'function' then hooksecurefunc(name, RenderNative) end
end
