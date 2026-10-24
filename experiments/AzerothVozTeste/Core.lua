-- Original 3.3.5 APIs only. This is a manual audio audition, not quest narration.
local frame = CreateFrame('Frame')
local previous, endsAt, db
local function Message(text)
    DEFAULT_CHAT_FRAME:AddMessage('|cff67d5ffTeste de vozes:|r ' .. text)
end
local function Stop()
    if previous then
        StopMusic()
        SetCVar('Sound_MusicVolume', previous.volume)
        SetCVar('Sound_EnableMusic', previous.enabled)
        previous, endsAt = nil, nil
    end
end
local function Play(name)
    local sample = AzerothVozTesteSamples[name]
    if not sample then Message('Amostra ausente no pacote.'); return end
    Stop()
    -- Stop the main addon's narration before using the shared music channel.
    if AzerothVoz and AzerothVoz.Stop then AzerothVoz.Stop() end
    previous = { volume = GetCVar('Sound_MusicVolume'), enabled = GetCVar('Sound_EnableMusic') }
    SetCVar('Sound_EnableMusic', '1')
    SetCVar('Sound_MusicVolume', tostring(db.volume))
    PlayMusic('Interface\\AddOns\\AzerothVozTeste\\audio\\' .. name .. '.mp3')
    endsAt = GetTime() + sample.duration + 0.25
    Message(sample.label .. ' — amostra extraída do patch. Não é a leitura de uma quest.')
end
frame:RegisterEvent('ADDON_LOADED')
frame:SetScript('OnEvent', function(self, event, name)
    if event == 'PLAYER_LOGOUT' then Stop(); return end
    if name ~= 'AzerothVozTeste' then return end
    local _, build = GetBuildInfo()
    if tostring(build) ~= '12340' then Message('Este teste exige o cliente build 12340.'); return end
    AzerothVozTesteDB = AzerothVozTesteDB or {}
    db = AzerothVozTesteDB
    db.volume = math.max(0, math.min(1, tonumber(db.volume) or 0.7))
    self:RegisterEvent('PLAYER_LOGOUT')
    SLASH_AZEROTHVOZTESTE1 = '/avozteste'
    SlashCmdList.AZEROTHVOZTESTE = function(input)
        local command, value = (input or ''):match('^%s*(%S+)%s*(.-)%s*$')
        command = string.lower(command or '')
        if command == 'jaina' or command == 'thrall' then Play(command)
        elseif command == 'parar' then Stop()
        elseif command == 'volume' then
            local number = tonumber(value)
            if not number or number < 0 or number > 100 then Message('Use /avozteste volume 70 (0 a 100).'); return end
            db.volume = number / 100
            if previous then SetCVar('Sound_MusicVolume', tostring(db.volume)) end
            Message('Volume: ' .. tostring(number) .. '%.')
        else Message('/avozteste jaina | thrall | parar | volume 70') end
    end
    Message('Carregado. Digite /avozteste jaina e depois /avozteste thrall.')
end)
frame:SetScript('OnUpdate', function()
    if endsAt and GetTime() >= endsAt then Stop() end
end)
