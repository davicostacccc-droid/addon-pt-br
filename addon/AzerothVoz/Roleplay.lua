-- Original 3.3.5 PlayerModel: no ModelScene, camera movement or game automation.
local A = AzerothVoz

local function Safe(model, method, ...)
    if not model or type(model[method]) ~= 'function' then return false end
    return pcall(model[method], model, ...)
end

local function Button(parent, text, x, callback)
    local b = CreateFrame('Button', nil, parent, 'UIPanelButtonTemplate')
    b:SetWidth(94); b:SetHeight(24); b:SetPoint('BOTTOMLEFT', x, 18)
    b:SetText(text); b:SetScript('OnClick', callback)
    return b
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
    f.state:SetText(active and 'NARRANDO' or A.lastStopReason == 'finished' and 'NARRAÇÃO CONCLUÍDA' or 'LEITURA — use Repetir para ouvir')
    if not active and A.lastStopReason == 'finished' then f.progress:SetValue(1) end
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

function A.CreateRoleplay()
    local shade = CreateFrame('Frame', nil, UIParent)
    shade:SetFrameStrata('HIGH'); shade:SetAllPoints(UIParent); shade:EnableMouse(false)
    shade:SetBackdrop({ bgFile = 'Interface\\Buttons\\WHITE8X8' })
    shade:SetBackdropColor(0, 0, 0, 0.24); shade:Hide()
    local f = CreateFrame('Frame', 'AzerothVozRoleplay', UIParent)
    A.roleplay = f; f.shade = shade
    f:SetWidth(720); f:SetHeight(370); f:SetPoint('CENTER', 0, 35)
    f:SetFrameStrata('DIALOG'); f:EnableMouse(true); f:SetMovable(true); f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart', function(self) self:StartMoving() end)
    f:SetScript('OnDragStop', function(self) self:StopMovingOrSizing() end)
    f:SetBackdrop({ bgFile = 'Interface\\DialogFrame\\UI-DialogBox-Background',
        edgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border', tile = true, tileSize = 32,
        edgeSize = 16, insets = { left = 5, right = 5, top = 5, bottom = 5 } })
    f:SetBackdropColor(0.04, 0.035, 0.025, 0.97); f:SetBackdropBorderColor(0.7, 0.53, 0.24, 1)
    local brand = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormalSmall')
    brand:SetPoint('TOPLEFT', 22, -18); brand:SetText('AZEROTHVOZ  |  HISTÓRIAS DE AZEROTH')
    f.speakerName = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
    f.speakerName:SetPoint('TOPLEFT', 242, -38); f.speakerName:SetWidth(445); f.speakerName:SetJustifyH('LEFT')
    f.chapter = f:CreateFontString(nil, 'OVERLAY', 'GameFontHighlightSmall')
    f.chapter:SetPoint('TOPLEFT', 242, -66); f.chapter:SetWidth(445); f.chapter:SetJustifyH('LEFT')
    f.fallback = f:CreateTexture(nil, 'ARTWORK')
    f.fallback:SetWidth(110); f.fallback:SetHeight(110); f.fallback:SetPoint('TOPLEFT', 64, -102)
    f.fallback:SetTexture('Interface\\Icons\\INV_Misc_QuestionMark')
    local ok, model = pcall(CreateFrame, 'PlayerModel', nil, f)
    if ok and model then
        f.model = model; model:SetWidth(204); model:SetHeight(242); model:SetPoint('TOPLEFT', 18, -46)
        model:EnableMouse(false); model:Hide()
        pcall(model.SetScript, model, 'OnAnimFinished', function(self)
            if f:IsShown() and f.modelReady and A.playing and A.current and A.playing == A.current.record then
                Safe(self, 'SetSequence', 60)
            end
        end)
    end
    local scroll = CreateFrame('ScrollFrame', 'AzerothVozRoleplayScroll', f, 'UIPanelScrollFrameTemplate')
    scroll:SetPoint('TOPLEFT', 242, -94); scroll:SetPoint('BOTTOMRIGHT', -37, 94)
    local body = CreateFrame('Frame', nil, scroll); body:SetWidth(422); body:SetHeight(1)
    scroll:SetScrollChild(body)
    f.text = body:CreateFontString(nil, 'OVERLAY', 'GameFontHighlight')
    f.text:SetPoint('TOPLEFT'); f.text:SetWidth(416); f.text:SetJustifyH('LEFT')
    f.scroll, f.body = scroll, body
    f.state = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormalSmall')
    f.state:SetPoint('BOTTOMLEFT', 242, 72); f.state:SetWidth(420); f.state:SetJustifyH('LEFT')
    f.progress = CreateFrame('StatusBar', nil, f)
    f.progress:SetPoint('BOTTOMLEFT', 242, 60); f.progress:SetWidth(430); f.progress:SetHeight(4)
    f.progress:SetStatusBarTexture('Interface\\TargetingFrame\\UI-StatusBar')
    f.progress:SetStatusBarColor(0.85, 0.64, 0.28); f.progress:SetMinMaxValues(0, 1); f.progress:SetValue(0)
    local hint = f:CreateFontString(nil, 'OVERLAY', 'GameFontHighlightSmall')
    hint:SetPoint('BOTTOMLEFT', 22, 53); hint:SetWidth(200)
    hint:SetText('Aceitar e recompensas:\nuse a janela da missão.')
    f.repeatButton = Button(f, 'Repetir', 242, function() A.Play(A.current and A.current.record) end)
    f.stopButton = Button(f, 'Parar', 344, A.Stop)
    f.minimizeButton = Button(f, 'Minimizar', 446, A.DismissRoleplay)
    f.modeButton = Button(f, 'Modo normal', 548, function()
        A.db.roleplay = false; A.DismissRoleplay()
    end)
    f:SetScript('OnUpdate', function(self, elapsed)
        if not self:IsShown() then return end
        self.updateIn = (self.updateIn or 0) - elapsed
        if self.updateIn > 0 then return end
        self.updateIn = 0.05
        local alpha = math.min(1, (GetTime() - (self.openedAt or GetTime())) / 0.22)
        self:SetAlpha(alpha); self.shade:SetAlpha(alpha)
        local speaker = A.current and A.current.speaker
        if self.modelReady and speaker and UnitGUID(speaker.unit) ~= speaker.guid then
            Safe(self.model, 'ClearModel'); self.model:Hide(); self.fallback:Show()
            self.modelReady, self.waitingModel = false, nil
        end
        if self.waitingModel then
            local ready, path = Safe(self.model, 'GetModel')
            if ready and type(path) == 'string' and path ~= '' then
                self.waitingModel, self.modelReady = nil, true; self.fallback:Hide()
                self.talking = false
                A.RoleplayVoiceChanged()
            elseif GetTime() >= self.waitingModel then
                self.waitingModel = nil; self.model:Hide()
            end
        end
        if A.playing and A.current and A.playing == A.current.record and A.startedAt then
            self.progress:SetValue(math.min(1, (GetTime() - A.startedAt) / A.playing.duration))
        end
    end)
    f:Hide()
end

function A.ShowRoleplay()
    local current, f = A.current, A.roleplay
    if not f or not current or not current.record or current.rpDismissed then return false end
    if UnitAffectingCombat and UnitAffectingCombat('player') then return false end
    if f.bound ~= current or not f:IsShown() then
        f.bound = current; f.openedAt = GetTime(); f.updateIn = 0
        f.speakerName:SetText(current.speaker and current.speaker.name or 'História de Azeroth')
        f.chapter:SetText(current.record.title or 'Diálogo')
        local text = A.Expand(current.record.translation)
        if current.record.objectives then text = text .. '\n\nObjetivos:\n' .. A.Expand(current.record.objectives) end
        f.text:SetText(text); f.body:SetHeight(math.max(1, f.text:GetStringHeight() + 10)); f.scroll:SetVerticalScroll(0)
        f.progress:SetValue(0); f:SetAlpha(0); f.shade:SetAlpha(0)
        if UIParent.GetWidth and f.SetScale then
            f:SetScale(math.min(1, math.max(0.5, ((UIParent:GetWidth() or 1024) - 24) / 720)))
        end
        f:Show(); f.shade:Show(); A.BindRoleplayModel()
    end
    A.RoleplayVoiceChanged()
    return true
end
