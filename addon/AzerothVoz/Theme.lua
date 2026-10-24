-- Modern, self-contained styling using only original 3.3.5 primitives.
local A = AzerothVoz
local T = { font = 'Fonts\\ARIALN.TTF', accent = { 0.86, 0.72, 0.47 },
    text = { 0.93, 0.95, 0.98 }, muted = { 0.57, 0.65, 0.74 } }
A.Theme = T

function T.Surface(frame, alpha)
    frame:SetBackdrop({ bgFile = 'Interface\\Buttons\\WHITE8X8', edgeFile = 'Interface\\Buttons\\WHITE8X8',
        edgeSize = 1, insets = { left = 1, right = 1, top = 1, bottom = 1 } })
    frame:SetBackdropColor(0.035, 0.049, 0.073, alpha or 0.98)
    frame:SetBackdropBorderColor(0.16, 0.20, 0.27, 0.9)
end

function T.Label(parent, size, color)
    local text = parent:CreateFontString(nil, 'OVERLAY')
    text:SetFont(T.font, size, '')
    text:SetTextColor(unpack(color or T.text)); text:SetJustifyH('LEFT')
    return text
end

function T.Block(parent, width, height, r, g, b, alpha)
    local t = parent:CreateTexture(nil, 'BACKGROUND')
    t:SetTexture('Interface\\Buttons\\WHITE8X8'); t:SetVertexColor(r, g, b, alpha or 1)
    t:SetWidth(width); t:SetHeight(height)
    return t
end

function T.Button(parent, label, width, callback, primary)
    local b = CreateFrame('Button', nil, parent)
    b:SetWidth(width); b:SetHeight(32); T.Surface(b, 1)
    b.label = T.Label(b, 16, primary and T.accent or T.text)
    b.label:SetPoint('CENTER'); b.label:SetJustifyH('CENTER'); b.label:SetText(label)
    b:SetScript('OnClick', callback)
    local function Rest(self)
        self:SetBackdropColor(0.065, 0.085, 0.115, 1)
        self:SetBackdropBorderColor(primary and 0.45 or 0.18, primary and 0.36 or 0.23, primary and 0.24 or 0.30, 1)
    end
    b:SetScript('OnEnter', function(self)
        self:SetBackdropColor(0.13, 0.17, 0.22, 1)
        self:SetBackdropBorderColor(T.accent[1], T.accent[2], T.accent[3], 1)
    end)
    b:SetScript('OnLeave', Rest); Rest(b)
    return b
end

function T.Toggle(parent, label, key, y, changed)
    local b = CreateFrame('Button', 'AzerothVoz_' .. key, parent)
    b:SetWidth(490); b:SetHeight(30); b:SetPoint('TOPLEFT', 24, y)
    b.label = T.Label(b, 18); b.label:SetPoint('LEFT', 0, 0); b.label:SetText(label)
    b.track = CreateFrame('Frame', nil, b)
    b.track:SetWidth(40); b.track:SetHeight(18); b.track:SetPoint('RIGHT', 0, 0); T.Surface(b.track)
    b.thumb = T.Block(b.track, 12, 12, 0.9, 0.93, 0.97, 1)
    local function Refresh(self)
        self.thumb:ClearAllPoints()
        self.thumb:SetPoint('LEFT', self.track, 'LEFT', A.db[key] and 25 or 3, 0)
        self.track:SetBackdropColor(A.db[key] and 0.34 or 0.10, A.db[key] and 0.28 or 0.13, A.db[key] and 0.19 or 0.18, 1)
    end
    b:SetScript('OnShow', Refresh)
    b:SetScript('OnClick', function(self)
        A.db[key] = not A.db[key]; Refresh(self)
        if changed then changed(key) end
    end)
    return b
end
