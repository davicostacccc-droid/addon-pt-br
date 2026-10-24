local A = AzerothVoz

local function Button(parent, text, x, callback)
    local b = CreateFrame('Button', nil, parent, 'UIPanelButtonTemplate')
    b:SetWidth(90); b:SetHeight(23); b:SetPoint('BOTTOMLEFT', x, 12)
    b:SetText(text); b:SetScript('OnClick', callback)
    return b
end

function A.CreateUI()
    local f = CreateFrame('Frame', 'AzerothVozReader', UIParent)
    A.reader = f
    f:SetWidth(370); f:SetHeight(330); f:SetPoint('CENTER', 320, 0)
    f:SetFrameStrata('DIALOG'); f:EnableMouse(true); f:SetMovable(true)
    f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart', function(self) self:StartMoving() end)
    f:SetScript('OnDragStop', function(self) self:StopMovingOrSizing() end)
    f:SetBackdrop({ bgFile = 'Interface\\DialogFrame\\UI-DialogBox-Background',
        edgeFile = 'Interface\\DialogFrame\\UI-DialogBox-Border', tile = true,
        tileSize = 32, edgeSize = 32, insets = { left = 10, right = 10, top = 10, bottom = 10 } })
    f.heading = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
    f.heading:SetPoint('TOPLEFT', 20, -20); f.heading:SetWidth(320)
    local scroll = CreateFrame('ScrollFrame', 'AzerothVozScroll', f, 'UIPanelScrollFrameTemplate')
    scroll:SetPoint('TOPLEFT', 20, -60); scroll:SetPoint('BOTTOMRIGHT', -35, 45)
    local body = CreateFrame('Frame', nil, scroll); body:SetWidth(310); body:SetHeight(1)
    scroll:SetScrollChild(body)
    f.text = body:CreateFontString(nil, 'OVERLAY', 'GameFontHighlight')
    f.text:SetPoint('TOPLEFT'); f.text:SetWidth(305); f.text:SetJustifyH('LEFT')
    f.body, f.scroll = body, scroll
    Button(f, 'Repetir', 15, function() A.Play(A.current and A.current.record) end)
    Button(f, 'Parar', 110, A.Stop)
    Button(f, 'Fechar', 205, function() A.Stop(); f:Hide() end)
    f:Hide()

    local controls = CreateFrame('Frame', 'AzerothVozControls', UIParent)
    A.controls = controls
    controls:SetWidth(200); controls:SetHeight(44)
    controls:SetFrameStrata('DIALOG'); controls:SetBackdrop(f:GetBackdrop())
    Button(controls, 'Repetir', 5, function() A.Play(A.current and A.current.record) end)
    Button(controls, 'Parar', 100, A.Stop)
    controls:Hide()

    local options = CreateFrame('Frame', 'AzerothVozOptions', UIParent)
    options.name = 'AzerothVoz'
    local heading = options:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
    heading:SetPoint('TOPLEFT', 16, -16); heading:SetText('AzerothVoz — Português brasileiro')
    local function Check(label, key, y)
        local c = CreateFrame('CheckButton', 'AzerothVoz_' .. key, options, 'InterfaceOptionsCheckButtonTemplate')
        c:SetPoint('TOPLEFT', 20, y)
        _G[c:GetName() .. 'Text']:SetText(label)
        c:SetScript('OnShow', function(self) self:SetChecked(A.db[key]) end)
        c:SetScript('OnClick', function(self)
            A.db[key] = self:GetChecked() and true or false
            if not A.db.enabled or not A.db.voice then A.Stop() end
            if not A.db.enabled then A.Close() end
            if key == 'extraWindow' and A.current then A.UpdatePresentation(A.nativeFrame) end
        end)
    end
    Check('Ativar tradução', 'enabled', -55)
    Check('Ativar dublagem', 'voice', -90)
    Check('Registrar falas sem tradução (limite: 1.000)', 'capture', -125)
    Check('Mostrar também a janela extra de tradução', 'extraWindow', -160)
    local slider = CreateFrame('Slider', 'AzerothVozVolume', options, 'OptionsSliderTemplate')
    slider:SetPoint('TOPLEFT', 25, -200); slider:SetWidth(260)
    slider:SetMinMaxValues(0, 1); slider:SetValueStep(0.05)
    _G[slider:GetName() .. 'Low']:SetText('0%')
    _G[slider:GetName() .. 'High']:SetText('100%')
    _G[slider:GetName() .. 'Text']:SetText('Volume da narração (canal Música)')
    slider:SetScript('OnShow', function(self) self:SetValue(A.db.volume) end)
    slider:SetScript('OnValueChanged', function(self, value)
        A.db.volume = value
        if A.playing then SetCVar('Sound_MusicVolume', tostring(value)) end
    end)
    local note = options:CreateFontString(nil, 'OVERLAY', 'GameFontHighlight')
    note:SetPoint('TOPLEFT', 25, -250); note:SetWidth(480); note:SetJustifyH('LEFT')
    note:SetText('A narração usa o canal Música e restaura o volume ao terminar.\n\n/avoz previa: ouvir uma missão do pacote\n/avoz exportar: copiar falas pendentes\n/avoz parar: interromper a fala\n/avoz repetir: repetir a fala atual\n/avoz janela on ou off: janela extra\n\nPacotes novos: instale com o jogo fechado. Cliente alvo: 3.3.5a / 12340.')
    InterfaceOptions_AddCategory(options)
    A.options = options
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
end

-- Hide the duplicate only after a translated native frame is confirmed visible.
-- Previews, missing translations and replacement UIs retain the scrollable reader.
function A.UpdatePresentation(nativeFrame)
    local current = A.current
    local visible = current and current.record and current.event ~= 'DEMO' and nativeFrame
        and nativeFrame:IsShown()
    A.nativeFrame = visible and nativeFrame or nil
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
        local label = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
        label:SetPoint('TOP', 0, -20); label:SetText('Ctrl+C: copie e salve como capturas.json em UTF-8')
        local scroll = CreateFrame('ScrollFrame', 'AzerothVozExportScroll', f, 'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT', 20, -50); scroll:SetPoint('BOTTOMRIGHT', -40, 50)
        local edit = CreateFrame('EditBox', nil, scroll)
        edit:SetMultiLine(true); edit:SetFontObject(ChatFontNormal); edit:SetWidth(530)
        edit:SetAutoFocus(false); edit:SetMaxLetters(0)
        edit:SetScript('OnEscapePressed', function() f:Hide() end)
        scroll:SetScrollChild(edit); f.edit = edit
        Button(f, 'Fechar', 250, function() f:Hide() end)
    end
    A.exportFrame:Show(); A.exportFrame.edit:SetText(A.ExportJSON())
    A.exportFrame.edit:SetFocus(); A.exportFrame.edit:HighlightText()
end
