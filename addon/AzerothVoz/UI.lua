local A = AzerothVoz
local T = A.Theme

local function Button(parent, text, x, callback)
    local b = T.Button(parent, text, 94, callback)
    b:SetPoint('BOTTOMLEFT', x, 12)
    return b
end

function A.CreateUI()
    local f = CreateFrame('Frame', 'AzerothVozReader', UIParent)
    A.reader = f
    f:SetWidth(560); f:SetHeight(430); f:SetPoint('CENTER', 320, 0)
    f:SetFrameStrata('DIALOG'); f:EnableMouse(true); f:SetMovable(true)
    f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart', function(self) self:StartMoving() end)
    f:SetScript('OnDragStop', function(self) self:StopMovingOrSizing() end)
    T.Surface(f)
    f.heading = T.Label(f, 26)
    f.heading:SetPoint('TOPLEFT', 24, -24); f.heading:SetWidth(490)
    local scroll = CreateFrame('ScrollFrame', 'AzerothVozScroll', f, 'UIPanelScrollFrameTemplate')
    scroll:SetPoint('TOPLEFT', 24, -70); scroll:SetPoint('BOTTOMRIGHT', -42, 56)
    local body = CreateFrame('Frame', nil, scroll); body:SetWidth(480); body:SetHeight(1)
    scroll:SetScrollChild(body)
    f.text = T.Label(body, 20)
    f.text:SetPoint('TOPLEFT'); f.text:SetWidth(472)
    f.body, f.scroll = body, scroll
    Button(f, 'Repetir', 15, function() A.Play(A.current and A.current.record) end)
    Button(f, 'Parar', 120, A.Stop)
    Button(f, 'Fechar', 225, function() A.Stop(); f:Hide() end)
    f:Hide()

    local controls = CreateFrame('Frame', 'AzerothVozControls', UIParent)
    A.controls = controls
    controls:SetWidth(220); controls:SetHeight(56)
    controls:SetFrameStrata('DIALOG'); T.Surface(controls)
    Button(controls, 'Repetir', 5, function() A.Play(A.current and A.current.record) end)
    Button(controls, 'Parar', 110, A.Stop)
    controls:Hide()

    local options = CreateFrame('Frame', 'AzerothVozSettings', UIParent)
    options:SetWidth(550); options:SetHeight(590); options:SetPoint('CENTER')
    options:SetFrameStrata('FULLSCREEN_DIALOG'); options:EnableMouse(true)
    T.Surface(options)
    local heading = T.Label(options, 30)
    heading:SetPoint('TOPLEFT', 24, -18); heading:SetText('AzerothVoz')
    local subtitle = T.Label(options, 16, T.muted)
    subtitle:SetPoint('TOPLEFT', 25, -56); subtitle:SetText('Sua história. No seu idioma.')
    local function Section(label, y)
        local text = T.Label(options, 13, T.accent)
        text:SetPoint('TOPLEFT', 24, y); text:SetText(label)
    end
    local function Changed(key)
        if not A.db.enabled or not A.db.voice then A.Stop() end
        if not A.db.enabled then A.Close() end
        if (key == 'roleplay' or key == 'extraWindow') and A.current then
            A.current.rpDismissed = nil; A.UpdatePresentation(A.nativeFrame)
        end
        if key == 'rpModel' and A.BindRoleplayModel then A.BindRoleplayModel() end
    end
    Section('APRESENTAÇÃO', -92)
    T.Toggle(options, 'Cena de diálogo', 'roleplay', -112, Changed)
    T.Toggle(options, 'Personagem em 3D', 'rpModel', -148, Changed)
    T.Toggle(options, 'Janela de leitura adicional', 'extraWindow', -184, Changed)
    Section('NARRAÇÃO', -234)
    T.Toggle(options, 'Ouvir as falas', 'voice', -254, Changed)
    local slider = CreateFrame('Slider', 'AzerothVozVolume', options, 'OptionsSliderTemplate')
    slider:SetPoint('TOPLEFT', 30, -314); slider:SetWidth(340)
    slider:SetMinMaxValues(0, 1); slider:SetValueStep(0.05)
    _G[slider:GetName() .. 'Low']:SetText('0%')
    _G[slider:GetName() .. 'High']:SetText('100%')
    _G[slider:GetName() .. 'Text']:SetText('Volume da voz')
    slider:SetScript('OnShow', function(self) self:SetValue(A.db.volume) end)
    slider:SetScript('OnValueChanged', function(self, value)
        A.db.volume = value
        if A.playing then SetCVar('Sound_MusicVolume', tostring(value)) end
    end)
    Section('TRADUÇÃO', -364)
    T.Toggle(options, 'Ativar AzerothVoz', 'enabled', -384, Changed)
    T.Toggle(options, 'Guardar falas ainda não traduzidas', 'capture', -420, Changed)
    local note = T.Label(options, 15, T.muted)
    note:SetPoint('TOPLEFT', 24, -478); note:SetWidth(490)
    note:SetText('Use Anterior e Próxima para ler no seu ritmo. Automático acompanha a duração da fala de forma aproximada.\n\n/avoz centralizar reposiciona a cena.\nTextos da beta podem precisar de revisão.')
    local close = T.Button(options, 'Fechar', 72, function() options:Hide() end)
    close:SetPoint('TOPRIGHT', -18, -18)
    A.settings = options; options:Hide()
    if UISpecialFrames then table.insert(UISpecialFrames, 'AzerothVozSettings') end
    -- The original options container is about 413 x 428 units: use a launcher.
    local category = CreateFrame('Frame', nil, UIParent); category.name = 'AzerothVoz'
    T.Surface(category)
    local title = T.Label(category, 26); title:SetPoint('TOPLEFT', 24, -24); title:SetText('AzerothVoz')
    local intro = T.Label(category, 17, T.muted); intro:SetPoint('TOPLEFT', 24, -66); intro:SetWidth(350)
    intro:SetText('Personalize a apresentação, a voz e a tradução no painel do AzerothVoz.')
    local open = T.Button(category, 'Abrir configurações', 220, function() A.OpenOptions() end)
    open:SetPoint('TOPLEFT', 24, -126)
    InterfaceOptions_AddCategory(category); A.options = category
    if A.CreateRoleplay then A.CreateRoleplay() end
end

function A.OpenOptions()
    if not A.settings then return end
    if InterfaceOptionsFrame and InterfaceOptionsFrame:IsShown() then InterfaceOptionsFrame:Hide() end
    local w, h = UIParent:GetWidth() or 1280, UIParent:GetHeight() or 720
    A.settings:SetScale(math.max(0.5, math.min(w * 0.42 / 550, h * 0.58 / 590)))
    A.settings:ClearAllPoints(); A.settings:SetPoint('CENTER', UIParent, 'CENTER', 0, 0); A.settings:Show()
end

function A.ShowLine(record, source, title)
    A.nativeFrame = nil
    A.controls:Hide()
    local f = A.reader
    f.heading:SetText(record and (record.title or title or 'Diálogo') or 'Tradução pendente')
    local text = record and A.Expand(record.translation) or
        ('Esta fala ainda não está no pacote. Use /avoz exportar para prepará-la.\n\nOriginal:\n' .. source)
    if record and record.objectives then text = text .. '\n\nObjetivos:\n' .. A.Expand(record.objectives) end
    f.text:SetText(text); f.body:SetHeight(math.max(1, f.text:GetStringHeight() + 10))
    f.scroll:SetVerticalScroll(0); f:Show()
    A.UpdatePresentation(nil)
end

-- Hide the duplicate only after a translated native frame is confirmed visible.
-- Previews, missing translations and replacement UIs retain the scrollable reader.
function A.UpdatePresentation(nativeFrame)
    local current = A.current
    local visible = current and current.record and current.event ~= 'DEMO' and nativeFrame
        and nativeFrame:IsShown()
    A.nativeFrame = visible and nativeFrame or nil
    if A.db.roleplay and A.ShowRoleplay and A.ShowRoleplay() then
        A.controls:Hide(); A.reader:Hide(); return
    end
    if A.HideRoleplay then A.HideRoleplay() end
    if visible then
        if A.db.extraWindow then
            A.controls:Hide(); A.reader:Show()
        else
            A.reader:Hide()
            A.controls:ClearAllPoints()
            A.controls:SetPoint('TOPLEFT', nativeFrame, 'BOTTOMLEFT', 0, -2)
            A.controls:Show()
        end
    else
        A.controls:Hide()
        if current then A.reader:Show() end
    end
end

local nativeChanges = {}
function A.NativeText(widget, text)
    if not widget or not widget.SetText or not widget.GetText then return false end
    local before = widget:GetText()
    local saved = nativeChanges[widget]
    if not saved then saved = { before = before }; nativeChanges[widget] = saved
    elseif before ~= saved.after then saved.before = before end
    saved.after = text
    widget:SetText(text)
    return true
end

function A.RestoreNative()
    for widget, saved in pairs(nativeChanges) do
        -- Do not overwrite a newer update from Blizzard or another addon.
        if widget:GetText() == saved.after then widget:SetText(saved.before or '') end
    end
    nativeChanges = {}
end

function A.TranslateLabels(event)
    local labels
    if event == 'GOSSIP_SHOW' then
        labels = { GossipFrameGreetingGoodbyeButton = 'Até mais' }
    else
        labels = {
            QuestInfoDescriptionHeader = 'Descrição', QuestInfoObjectivesHeader = 'Objetivos',
            QuestInfoRewardsHeader = 'Recompensas', QuestFrameAcceptButton = 'Aceitar',
            QuestFrameDeclineButton = 'Recusar', QuestFrameCompleteButton = 'Continuar',
            QuestFrameCompleteQuestButton = 'Concluir missão', QuestFrameCancelButton = 'Cancelar',
            QuestFrameGoodbyeButton = 'Até mais', QuestFrameGreetingGoodbyeButton = 'Até mais',
            QuestProgressRequiredItemsText = 'Itens necessários',
            QuestProgressRequiredMoneyText = 'Dinheiro necessário',
            CurrentQuestsText = 'Missões em andamento', AvailableQuestsText = 'Missões disponíveis',
            QuestInfoItemChooseText = event == 'QUEST_DETAIL' and 'Você poderá escolher uma destas recompensas:'
                or 'Escolha uma destas recompensas:',
            QuestInfoItemReceiveText = 'Você também receberá:',
        }
    end
    for name, text in pairs(labels) do A.NativeText(_G[name], text) end
end

local function JsonString(s)
    return '"' .. tostring(s):gsub('[%z\1-\31\\"]', function(c)
        if c == '"' then return '\\"' end
        if c == '\\' then return '\\\\' end
        return string.format('\\u%04x', string.byte(c))
    end) .. '"'
end

function A.ExportJSON()
    local rows = {}
    for _, r in pairs(A.captures.lines) do
        local fields = {}
        for _, k in ipairs({ 'event', 'npc', 'source', 'title', 'questID', 'locale' }) do
            if r[k] ~= nil then table.insert(fields, JsonString(k) .. ':' ..
                (type(r[k]) == 'number' and tostring(r[k]) or JsonString(r[k]))) end
        end
        table.insert(rows, '{' .. table.concat(fields, ',') .. '}')
    end
    return '{"version":1,"lines":[' .. table.concat(rows, ',') .. ']}'
end

function A.Export()
    if not A.exportFrame then
        local f = CreateFrame('Frame', 'AzerothVozExport', UIParent)
        A.exportFrame = f
        f:SetWidth(600); f:SetHeight(400); f:SetPoint('CENTER'); f:SetFrameStrata('FULLSCREEN_DIALOG')
        f:SetBackdrop(A.reader:GetBackdrop())
        local label = T.Label(f, 18)
        label:SetPoint('TOP', 0, -20); label:SetText('Ctrl+C: copie e salve como capturas.json em UTF-8')
        local scroll = CreateFrame('ScrollFrame', 'AzerothVozExportScroll', f, 'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT', 20, -50); scroll:SetPoint('BOTTOMRIGHT', -40, 50)
        local edit = CreateFrame('EditBox', nil, scroll)
        edit:SetMultiLine(true); edit:SetFont(T.font, 16, ''); edit:SetWidth(530)
        edit:SetAutoFocus(false); edit:SetMaxLetters(0)
        edit:SetScript('OnEscapePressed', function() f:Hide() end)
        scroll:SetScrollChild(edit); f.edit = edit
        Button(f, 'Fechar', 250, function() f:Hide() end)
    end
    A.exportFrame:Show(); A.exportFrame.edit:SetText(A.ExportJSON())
    A.exportFrame.edit:SetFocus(); A.exportFrame.edit:HighlightText()
end
