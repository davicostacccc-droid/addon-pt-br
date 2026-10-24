-- Lua 5.1 / WoW 3.3.5a. No HTTP, file I/O or modern C_* APIs.
AzerothVoz = { version = '0.2.1', index = {}, templates = {}, quests = {}, count = 0 }
local A = AzerothVoz

function A.Normalize(text)
    local lowered = (text or ''):gsub('[A-Z]', function(c) return string.char(c:byte() + 32) end)
    return (lowered:gsub('[ \009\010\011\012\013]+', ' '):gsub('^ ', ''):gsub(' $', ''))
end

function A.Hash(text)
    local h = 5381
    for i = 1, #text do h = (h * 33 + text:byte(i)) % 2147483647 end
    return tostring(h)
end

function A.Key(event, npc, text)
    return event .. ':' .. tostring(npc or 0) .. ':' .. A.Hash(A.Normalize(text))
end

function A.Register(record)
    local key = A.Key(record.event, record.npc, record.source)
    A.index[key] = A.index[key] or {}
    table.insert(A.index[key], record)
    if record.questID then
        A.quests[record.questID] = A.quests[record.questID] or {}
        A.quests[record.questID][record.event] = record
    end
    if record.source:find('$', 1, true) then
        local group = record.event .. ':' .. tostring(record.npc)
        A.templates[group] = A.templates[group] or {}
        table.insert(A.templates[group], record)
    end
end

function A.Lookup(event, npc, source)
    for _, r in ipairs(A.index[A.Key(event, npc, source)] or {}) do
        -- Hashes only select a bucket. A collision must never play another line.
        if A.Normalize(r.source) == A.Normalize(source) then return r end
    end
    -- Check only this NPC/event's templates, resolving known player markers.
    -- Everything else must still match the entire English source text.
    for _, r in ipairs(A.templates[event .. ':' .. tostring(npc)] or {}) do
        if A.Normalize(A.ResolveSource(r.source)) == A.Normalize(source) then return r end
    end
end

function A.ResolveSource(text)
    text = text:gsub('%$[bB]', '\n')
    text = text:gsub('%$[gG]([^:;]*):([^;]*);', function(male, female)
        return UnitSex('player') == 3 and female or male
    end)
    return (text:gsub('%$([nNcCrR])', function(token)
        token = string.lower(token)
        if token == 'n' then return UnitName('player') or '' end
        if token == 'c' then return UnitClass('player') or '' end
        return UnitRace('player') or ''
    end))
end

function A.Tokenize(text)
    local name = UnitName('player')
    if name and name ~= '' then
        -- Literal search also handles UTF-8 names, without locale-dependent
        -- frontier patterns and without replacing a name inside another word.
        local function IsWord(byte)
            return byte and ((byte >= 48 and byte <= 57) or (byte >= 65 and byte <= 90)
                or (byte >= 97 and byte <= 122) or byte >= 128)
        end
        local parts, pos = {}, 1
        while true do
            local first, last = text:find(name, pos, true)
            if not first then break end
            table.insert(parts, text:sub(pos, first - 1))
            table.insert(parts, (not IsWord(text:byte(first - 1)) and not IsWord(text:byte(last + 1)))
                and '$n' or name)
            pos = last + 1
        end
        table.insert(parts, text:sub(pos))
        text = table.concat(parts)
    end
    return text
end

function A.Expand(text)
    return (text or ''):gsub('%$[nN]', function() return UnitName('player') or 'aventureiro' end)
end

function A.NpcID(guid)
    -- Old 64-bit hex GUID: 0xF130 + six hex digits of creature entry + spawn.
    if type(guid) ~= 'string' or #guid ~= 18 then return nil end
    local prefix = guid:sub(1, 6):upper()
    if prefix ~= '0XF130' and prefix ~= '0XF150' then return nil end
    return tonumber(guid:sub(7, 12), 16)
end

function A.Message(text)
    DEFAULT_CHAT_FRAME:AddMessage('|cff67d5ffAzerothVoz:|r ' .. text)
end

function A.Init()
    AzerothVozDB = AzerothVozDB or {}
    A.db = AzerothVozDB
    local defaults = { enabled = true, voice = true, volume = 0.7, capture = true, extraWindow = false }
    for k, v in pairs(defaults) do if A.db[k] == nil then A.db[k] = v end end
    A.db.volume = math.max(0, math.min(1, tonumber(A.db.volume) or 0.7))
    AzerothVozCaptures = AzerothVozCaptures or { version = 1, lines = {} }
    A.captures = AzerothVozCaptures
    A.captures.lines = A.captures.lines or {}
    for _ in pairs(A.captures.lines) do A.count = A.count + 1 end
    -- Best-effort recovery if a temporary snapshot was persisted previously.
    A.Stop()
end

function A.Stop()
    if A.playing and StopMusic then StopMusic() end
    A.playing, A.endsAt = nil, nil
    if A.db and A.db.musicBefore then
        local old = A.db.musicBefore
        SetCVar('Sound_MusicVolume', old.volume)
        SetCVar('Sound_EnableMusic', old.enabled)
        A.db.musicBefore = nil
    end
end

function A.Play(record)
    A.Stop()
    if not A.db.enabled or not A.db.voice or not record or not record.audio then return end
    if not PlayMusic or not StopMusic then
        A.Message('API de música indisponível neste cliente.'); return
    end
    -- The 3.3.5 API provides no reliable per-file sound handle. Music gives
    -- us a stoppable channel and volume control, shared with in-game music.
    A.db.musicBefore = { volume = GetCVar('Sound_MusicVolume'), enabled = GetCVar('Sound_EnableMusic') }
    SetCVar('Sound_EnableMusic', '1')
    SetCVar('Sound_MusicVolume', tostring(A.db.volume))
    PlayMusic('Interface\\AddOns\\AzerothVoz\\' .. record.audio)
    A.playing = record
    A.endsAt = GetTime() + record.duration + 0.25
end

function A.Capture(event, npc, text, title, questID)
    if not A.db.capture or text == '' then return end
    local key = A.Key(event, npc, text)
    local base, suffix = key, 1
    while A.captures.lines[key] and A.captures.lines[key].source ~= text do
        key = base .. ':' .. suffix; suffix = suffix + 1
    end
    if not A.captures.lines[key] and A.count >= 1000 then return end
    if not A.captures.lines[key] then A.count = A.count + 1 end
    -- No structured character name, account path or full GUID is exported.
    A.captures.lines[key] = { event = event, npc = npc or 0, source = text,
        title = title or '', questID = questID, locale = GetLocale() }
end

function A.Handle(event, npc, source, title, questID)
    if not A.db or not A.db.enabled or not npc or not source or source == '' then
        A.Stop(); A.current = nil
        if A.reader then A.reader:Hide() end
        if A.controls then A.controls:Hide() end
        if A.RestoreNative then A.RestoreNative() end
        A.nativeFrame = nil
        return
    end
    local text = A.Tokenize(source)
    local record = A.Lookup(event, npc, text) or A.Lookup(event, npc, source)
    local key = A.Key(event, npc, text)
    if A.current and A.current.key == key and A.current.source == text then return end
    A.Stop()
    if A.RestoreNative then A.RestoreNative() end
    A.current = { key = key, record = record, source = text, event = event }
    if not record then A.Capture(event, npc, text, title, questID) end
    if A.ShowLine then A.ShowLine(record, source, title) end
    if record then A.Play(record) end
end

function A.Preview(questID)
    local record = A.quests[questID] and A.quests[questID].QUEST_DETAIL
    if not record then A.Message('Esta missão não está no pacote instalado.'); return end
    if not A.db.enabled then A.Message('Ative o addon com /avoz on.'); return end
    if A.RestoreNative then A.RestoreNative() end
    A.pending = nil
    A.current = { record = record, event = 'DEMO' }
    if A.ShowLine then A.ShowLine(record, A.ResolveSource(record.source), record.title) end
    A.Play(record)
end
