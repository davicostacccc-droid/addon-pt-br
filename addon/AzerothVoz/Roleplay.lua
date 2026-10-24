-- Original 3.3.5 PlayerModel: no ModelScene, camera movement or game automation.
local A = AzerothVoz

local function Safe(model, method, ...)
    if not model or type(model[method]) ~= 'function' then return false end
    return pcall(model[method], model, ...)
end

function A.HideRoleplay()
    local f = A.roleplay
    if not f then return end
    f:Hide(); f.shade:Hide(); f.waitingModel = nil
    if f.model then
        Safe(f.model, 'SetSequence', 0)
        Safe(f.model, 'ClearModel'); f.model:Hide()
    end
    f.modelReady, f.talking = false, false
end

function A.DismissRoleplay()
    if A.current then A.current.rpDismissed = true end
    A.HideRoleplay()
    if A.current then A.UpdatePresentation(A.nativeFrame) end
end

function A.RoleplayVoiceChanged()
    local f = A.roleplay
    if not f or not f:IsShown() then return end
    local active = A.playing and A.current and A.playing == A.current.record
    if active and not f.wasPlaying then A.RoleplayText(false) end
    f.wasPlaying = active and true or false
    f.state:SetText(active and 'EM NARRAÇÃO' or A.lastStopReason == 'finished' and 'CONCLUÍDA' or 'LEITURA')
    if not active and A.lastStopReason == 'finished' then
        f.progress:SetValue(1); if not f.manualPage then A.SyncRoleplayPage(1) end
    end
    if f.modelReady and active ~= f.talking then
        -- 60 = ANIM_EMOTE_TALK, 0 = ANIM_STAND in WotLK AnimationData.
        Safe(f.model, 'SetSequence', active and 60 or 0)
    end
    f.talking = active and true or false
end

function A.BindRoleplayModel()
    local f = A.roleplay
    if not f then return end
    f.fallback:Show(); f.modelReady, f.waitingModel, f.talking = false, nil, false
    if f.model then Safe(f.model, 'ClearModel'); f.model:Hide() end
    local current = A.current
    local speaker = current and current.speaker
    local npc = current and current.record and current.record.npc
    if not f:IsShown() or not A.db.rpModel or not f.model or not speaker or not npc or npc == 0 then return end
    -- The unit must still be the one captured by the dialogue event. Never
    -- silently substitute the player, current target or an unrelated NPC.
    if UnitGUID(speaker.unit) ~= speaker.guid or A.NpcID(speaker.guid) ~= npc then return end
    if not Safe(f.model, 'SetUnit', speaker.unit) then return end
    Safe(f.model, 'SetCamera', 0); Safe(f.model, 'SetFacing', 0.15)
    f.model:Show(); f.waitingModel = GetTime() + 1
end


-- Byte-safe UTF-8 pagination. Raw pages reconstruct the original text exactly.
local function Characters(text)
    local n = 0
    for i = 1, #text do local b = text:byte(i); if b < 128 or b >= 192 then n = n + 1 end end
    return math.max(1, n)
end

function A.RoleplayPages(text, limit)
    text, limit = text or '', limit or 250
    local pages, start = {}, 1
    while start <= #text do
        local pos, score, lastBreak, lastSentence, started = start, 0, nil, nil, false
        while pos <= #text and score < limit do
            local byte = text:byte(pos)
            local size = byte < 128 and 1 or byte < 224 and 2 or byte < 240 and 3 or 4
            score = score + (byte == 10 and started and 50 or 1)
            if byte == 32 or byte == 10 or byte == 9 then
                lastBreak = pos
                local previous = text:byte(pos - 1)
                if score >= limit * 0.4 and (previous == 46 or previous == 33 or previous == 63) then lastSentence = pos end
            else started = true end
            pos = math.min(#text + 1, pos + size)
        end
        local finish = pos - 1
        if pos <= #text then
            if lastSentence and lastSentence > start then finish = lastSentence
            elseif lastBreak and lastBreak > start then finish = lastBreak end
        end
        table.insert(pages, text:sub(start, finish)); start = finish + 1
    end
    if #pages == 0 then pages[1] = '' end
    if #pages > 1 and Characters(pages[#pages]) < math.min(60, limit * 0.22) then
        local combined = pages[#pages - 1] .. pages[#pages]
        if Characters(combined) <= limit then
            pages[#pages - 1] = combined; table.remove(pages)
        else
            local pos, count, split = 1, 0, nil
            local target = Characters(combined) * 0.55
            while pos <= #combined and count < target do
                local byte = combined:byte(pos)
                if byte == 32 or byte == 10 then split = pos end
                pos = pos + (byte < 128 and 1 or byte < 224 and 2 or byte < 240 and 3 or 4); count = count + 1
            end
            if split and Characters(combined:sub(split + 1)) > limit then split = nil end
            split = split or pos - 1
            pages[#pages - 1], pages[#pages] = combined:sub(1, split), combined:sub(split + 1)
        end
    end
    return pages
end

function A.RoleplayPage(index, manual)
    local f = A.roleplay
    if not f or not f.pages then return end
    if manual then f.manualPage = true end
    index = math.max(1, math.min(#f.pages, index))
    if index ~= f.page then
        f.page = index; f.pageAt = GetTime(); f.text:SetAlpha(0)
        f.text:SetText((f.pages[index]:gsub('^%s+', ''):gsub('%s+$', '')))
    end
    f.pageLabel:SetText(string.format('%02d / %02d', index, #f.pages))
    f.autoButton.label:SetText(f.inObjectives and 'Voltar à fala' or f.manualPage and 'Retomar auto' or 'Automático')
end

function A.RoleplayText(objectives)
    local f = A.roleplay
    if not f then return end
    f.inObjectives = objectives and true or false
    local text = objectives and f.objectivesText or f.dialogueText
    f.pages, f.ends, f.page = A.RoleplayPages(text), {}, nil
    local total = 0
    for _, page in ipairs(f.pages) do total = total + Characters(page) end
    local current = 0
    for i, page in ipairs(f.pages) do current = current + Characters(page); f.ends[i] = current / total end
    f.manualPage = objectives and true or false
    f.objectivesButton.label:SetText(objectives and 'Voltar à fala' or 'Ver objetivos')
    A.RoleplayPage(1, false)
end

function A.SyncRoleplayPage(progress)
    local f = A.roleplay
    if not f or f.manualPage or f.inObjectives then return end
    local page = #f.pages
    for i, finish in ipairs(f.ends) do if progress <= finish then page = i; break end end
    A.RoleplayPage(page, false)
end

function A.CenterRoleplay()
    local f = A.roleplay
    if not f then return end
    local w = UIParent:GetWidth() or 1280
    local h = UIParent:GetHeight() or 720
    -- Relative UI dimensions also compensate for custom global UI scaling.
    f:SetScale(math.max(0.4, math.min(w * 0.68 / 1100, h * 0.44 / 440)))
    f:ClearAllPoints(); f:SetPoint('CENTER', UIParent, 'CENTER', 0, -h * 0.035)
end

function A.CreateRoleplay()
    local T = A.Theme
    local shade = CreateFrame('Frame', nil, UIParent)
    shade:SetFrameStrata('HIGH'); shade:SetAllPoints(UIParent); shade:EnableMouse(false)
    shade:SetBackdrop({ bgFile = 'Interface\\Buttons\\WHITE8X8' })
    shade:SetBackdropColor(0.008, 0.013, 0.025, 0.40); shade:Hide()
    local f = CreateFrame('Frame', 'AzerothVozScene', UIParent)
    A.roleplay = f; f.shade = shade
    f:SetWidth(1100); f:SetHeight(440); T.Surface(f, 0.985)
    f:SetFrameStrata('DIALOG'); f:EnableMouse(true); f:SetMovable(true); f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart', function(self) self:StartMoving() end)
    f:SetScript('OnDragStop', function(self) self:StopMovingOrSizing() end)
    local portrait = T.Block(f, 310, 438, 0.025, 0.037, 0.059, 1)
    portrait:SetPoint('TOPLEFT', 1, -1)
    local divider = T.Block(f, 1, 382, 0.17, 0.22, 0.30, 0.6)
    divider:SetPoint('TOPLEFT', 312, -28)
    local rule = T.Block(f, 36, 2, unpack(T.accent)); rule:SetPoint('TOPLEFT', 342, -30)
    f.state = T.Label(f, 13, T.accent); f.state:SetPoint('TOPLEFT', 390, -22)
    f.speakerName = T.Label(f, 32); f.speakerName:SetPoint('TOPLEFT', 342, -48); f.speakerName:SetWidth(650)
    f.chapter = T.Label(f, 18, T.muted); f.chapter:SetPoint('TOPLEFT', 342, -94); f.chapter:SetWidth(690)
    f.text = T.Label(f, 24); f.text:SetPoint('TOPLEFT', 342, -144); f.text:SetWidth(704); f.text:SetHeight(174)
    f.text:SetJustifyV('TOP')
    f.pageLabel = T.Label(f, 14, T.muted); f.pageLabel:SetPoint('BOTTOMLEFT', 438, 84)
    f.previousButton = T.Button(f, 'Anterior', 86, function() A.RoleplayPage((f.page or 1) - 1, true) end)
    f.previousButton:SetPoint('BOTTOMLEFT', 342, 76)
    f.nextButton = T.Button(f, 'Próxima', 86, function() A.RoleplayPage((f.page or 1) + 1, true) end)
    f.nextButton:SetPoint('BOTTOMLEFT', 506, 76)
    f.autoButton = T.Button(f, 'Automático', 116, function()
        if f.inObjectives then A.RoleplayText(false) end
        f.manualPage = false; A.RoleplayPage(f.page or 1, false)
    end)
    f.autoButton:SetPoint('BOTTOMLEFT', 604, 76)
    f.clock = T.Label(f, 14, T.muted); f.clock:SetPoint('BOTTOMRIGHT', -40, 83); f.clock:SetJustifyH('RIGHT')
    f.progress = CreateFrame('StatusBar', nil, f)
    f.progress:SetPoint('BOTTOMLEFT', 342, 61); f.progress:SetWidth(718); f.progress:SetHeight(2)
    f.progress:SetStatusBarTexture('Interface\\Buttons\\WHITE8X8')
    f.progress:SetStatusBarColor(unpack(T.accent)); f.progress:SetMinMaxValues(0, 1); f.progress:SetValue(0)
    f.repeatButton = T.Button(f, 'Ouvir do início', 148, function() A.Play(A.current and A.current.record) end, true)
    f.repeatButton:SetPoint('BOTTOMLEFT', 342, 16)
    f.stopButton = T.Button(f, 'Parar', 86, A.Stop); f.stopButton:SetPoint('BOTTOMLEFT', 500, 16)
    f.minimizeButton = T.Button(f, 'Minimizar', 106, A.DismissRoleplay); f.minimizeButton:SetPoint('BOTTOMLEFT', 596, 16)
    f.modeButton = T.Button(f, 'Modo padrão', 116, function() A.db.roleplay = false; A.DismissRoleplay() end)
    f.modeButton:SetPoint('BOTTOMRIGHT', -40, 16)
    f.objectivesButton = T.Button(f, 'Ver objetivos', 150, function() A.RoleplayText(not f.inObjectives) end)
    f.objectivesButton:SetPoint('BOTTOMLEFT', 78, 16)
    local brand = T.Label(f, 12, T.muted); brand:SetPoint('BOTTOMLEFT', 104, 62); brand:SetText('A Z E R O T H V O Z')
    f.fallback = T.Label(f, 21, T.muted); f.fallback:SetPoint('CENTER', f, 'TOPLEFT', 156, -205)
    f.fallback:SetWidth(230); f.fallback:SetJustifyH('CENTER'); f.fallback:SetText('A história continua')
    local ok, model = pcall(CreateFrame, 'PlayerModel', nil, f)
    if ok and model then
        f.model = model; model:SetWidth(302); model:SetHeight(362); model:SetPoint('TOPLEFT', 5, -14)
        model:EnableMouse(false); model:Hide()
        pcall(model.SetScript, model, 'OnAnimFinished', function(self)
            if f:IsShown() and f.modelReady and A.playing and A.current and A.playing == A.current.record then Safe(self, 'SetSequence', 60) end
        end)
    end
    f:SetScript('OnUpdate', function(self, elapsed)
        if not self:IsShown() then return end
        self.updateIn = (self.updateIn or 0) - elapsed; if self.updateIn > 0 then return end
        self.updateIn = 0.05
        local now = GetTime()
        local alpha = math.min(1, (now - (self.openedAt or now)) / 0.26)
        self:SetAlpha(alpha); self.shade:SetAlpha(alpha)
        self.text:SetAlpha(math.min(1, (now - (self.pageAt or now)) / 0.16))
        local speaker = A.current and A.current.speaker
        if self.modelReady and speaker and UnitGUID(speaker.unit) ~= speaker.guid then
            Safe(self.model, 'ClearModel'); self.model:Hide(); self.fallback:Show(); self.modelReady, self.waitingModel = false, nil
        end
        if self.waitingModel then
            local ready, path = Safe(self.model, 'GetModel')
            if ready and type(path) == 'string' and path ~= '' then
                self.waitingModel, self.modelReady = nil, true; self.fallback:Hide(); self.talking = false; A.RoleplayVoiceChanged()
            elseif now >= self.waitingModel then self.waitingModel = nil; self.model:Hide() end
        end
        if A.playing and A.current and A.playing == A.current.record and A.startedAt then
            local progress = math.min(1, (now - A.startedAt) / A.playing.duration)
            self.progress:SetValue(progress); A.SyncRoleplayPage(progress)
            local seconds = math.min(A.playing.duration, now - A.startedAt)
            self.clock:SetText(string.format('%02d:%02d / %02d:%02d', math.floor(seconds / 60), math.floor(seconds % 60),
                math.floor(A.playing.duration / 60), math.floor(A.playing.duration % 60)))
        end
    end)
    A.CenterRoleplay(); f:Hide()
end

function A.ShowRoleplay()
    local current, f = A.current, A.roleplay
    if not f or not current or not current.record or current.rpDismissed then return false end
    if UnitAffectingCombat and UnitAffectingCombat('player') then return false end
    if f.bound ~= current or not f:IsShown() then
        f.bound = current; f.openedAt = GetTime(); f.updateIn = 0; f.wasPlaying = false
        f.speakerName:SetText(current.speaker and current.speaker.name or 'História de Azeroth')
        f.chapter:SetText(current.record.title or 'Diálogo')
        f.dialogueText = A.Expand(current.record.translation)
        f.objectivesText = current.record.objectives and A.Expand(current.record.objectives) or nil
        if f.objectivesText then f.objectivesButton:Show() else f.objectivesButton:Hide() end
        A.RoleplayText(false); f.progress:SetValue(0); f.clock:SetText('')
        f:SetAlpha(0); f.shade:SetAlpha(0); A.CenterRoleplay()
        f:Show(); f.shade:Show(); A.BindRoleplayModel()
    end
    A.RoleplayVoiceChanged(); return true
end
