
require('addon')
local events = require('samp.events')
local sampev = require("samp.events")
local effil = require("effil")
local encoding = require("encoding")
local ini = require("inicfg")
local inicfg = require("inicfg")
local json = require("cjson")
local settings = ini.load(nil, "lesopilka\\lesopilka.txt")
local settings = settings.settings
local mystats = settings.mystats
local lastMessage = ""
local lastMessageTime = 0
local messageCooldown = 4
local token, chatid

encoding.default = "CP1251"
u8 = encoding.UTF8

if settings.token and settings.chatid then
    token, chatid = settings.token, settings.chatid
end

-- randomnick
 local randomnick = settings.randomnick
    if randomnick then
function setRandomNick()
    local data = {names = {}, surnames = {}}
    local filenames = {"settings\\names.txt", "settings\\surnames.txt"}
    for i = 1, #filenames do
        local file = io.open(filenames[i], "r")
        if not file then
            return
        end
        for line in file:lines() do
            line = line:gsub("%s", "")
            table.insert(i == 1 and data.names or data.surnames, line)
        end
        file:close()
    end
	math.randomseed(os.clock())
    setBotNick(("%s_%s"):format(data.names[math.random(1, #data.names)], data.surnames[math.random(1, #data.surnames)]))
	print(getBotNick())
    reconnect(1000)
end
end

-- local
local interiorVisits = {} -- Таблица для отслеживания количества посещений каждого интерьера
local usedProxy = {} -- used random proxys index
local PROXY_STATE = true -- current proxy state (false if not connected, true if connected or not proxys)
local alt = true
local gps = true
local timetp = 115
local steptp = 2

local time1 = 95
local timer = os.time()


function sampev.onSendPlayerSync(data)
    if key then
        data.keysData = key
        key = nil
    end
end

function sampev.onSetInterior(interior)
    if interior == 0 then
        newTask(function()
            wait(1500) -- Ожидание перед телепортацией
			sendTG("Заспавнилися! %0AИмя бота: " .. getBotNick() .. " Пароль: fsdahjfdsfajkhgurn  %0AСервер " .. getServerName() .. "")
			wait(15000)
            sendTG("Летит в нелюдное место %0AИмя бота: " .. getBotNick() .. " Пароль: fsdahjfdsfajkhgurn  %0AСервер " .. getServerName() .. "")			-- Ожидание перед телепортацией
            tp(1671.1110839844, -1638.4255371094, 22.522367477417) -- Телепортация к лесопилке
			wait(20000)
			sendTG("Спрятался от игроков! %0AИмя бота: " .. getBotNick() .. " Пароль: fsdahjfdsfajkhgurn  %0AСервер " .. getServerName() .. "")
        end)
    elseif interior == 999 then
        newTask(function()
            wait(500) -- Добавлена небольшая задержка перед телепортацией
            tp(-514.6973, -154.4233, 1057.4243)
            printk('BOT - БЕРУ ФОРМУ')
            sendTG("Беру форму !%0AАккаунт: " .. getBotNick() .. " Пароль: Sam_Mason  %0AСервер " .. getServerName() .. "%")
			wait(1500) -- Добавлена небольшая задержка перед телепортацией
        end) 
    end
end



function onUpdate()
	if os.time() - timer >= 8 then
		timer = os.time()
		sendKey(1024)
	end
end

function onRequestConnect()
	if not PROXY_STATE then return false end
	if no_connect then return false end
end


-- my function
function tp(x, y, z)
	coordStart(x, y, z, timetp, steptp, false)
end

function printk(text)
	print('TEST >> ' .. text .. ' << TEST')
end

function lesopilka()
	for k, v in pairs(getAllLabels()) do
		if v.text:find("Срубленное дерево") then
			x = v.position.x
			y = v.position.y
			z = v.position.z
		end
	end
	coordStart(x, y, z, timetp, steptp, false)
	printk('X: ' .. x .. ' | Y: ' .. y .. ' | Z: ' .. z .. ' - TELEPORT')
end

local ansi_decode = {[128] = "\208\130",[129] = "\208\131",[130] = "\226\128\154",[131] = "\209\147",[132] = "\226\128\158",[133] = "\226\128\166",[134] = "\226\128\160",[135] = "\226\128\161",[136] = "\226\130\172",[137] = "\226\128\176",[138] = "\208\137",[139] = "\226\128\185",[140] = "\208\138",[141] = "\208\140",[142] = "\208\139",[143] = "\208\143",[144] = "\209\146",[145] = "\226\128\152",[146] = "\226\128\153",[147] = "\226\128\156",[148] = "\226\128\157",[149] = "\226\128\162",[150] = "\226\128\147",[151] = "\226\128\148",[152] = "\194\152",[153] = "\226\132\162",[154] = "\209\153",[155] = "\226\128\186",[156] = "\209\154",[157] = "\209\156",[158] = "\209\155",[159] = "\209\159",[160] = "\194\160",[161] = "\209\142",[162] = "\209\158",[163] = "\208\136",[164] = "\194\164",[165] = "\210\144",[166] = "\194\166",[167] = "\194\167",[168] = "\208\129",[169] = "\194\169",[170] = "\208\132",[171] = "\194\171",[172] = "\194\172",[173] = "\194\173",[174] = "\194\174",[175] = "\208\135",[176] = "\194\176",[177] = "\194\177",[178] = "\208\134",[179] = "\209\150",[180] = "\210\145",[181] = "\194\181",[182] = "\194\182",[183] = "\194\183",[184] = "\209\145",[185] = "\226\132\150",[186] = "\209\148",[187] = "\194\187",[188] = "\209\152",[189] = "\208\133",[190] = "\209\149",[191] = "\209\151"}
function AnsiToUtf8(s)
    local r, b = "", ""
    for i = 1, s and s:len() or 0 do
        b = s:byte(i)
        if b < 128 then
            r = r .. string.char(b)
        else
            if b > 239 then
                r = r .. "\209" .. string.char(b - 112)
            elseif b > 191 then
                r = r .. "\208" .. string.char(b - 48)
            elseif ansi_decode[b] then
                r = r .. ansi_decode[b]
            else
                r = r .. "_"
            end
        end
    end
    return r
end

function threadHandle(runner, url, args, resolve, reject)
    local t = runner(url, args)
    local r = t:get(0)
    while not r do
        r = t:get(0)
        wait(0)
    end
    local status = t:status()
    if status == "completed" then
        local ok, result = r[1], r[2]
        if ok then
            resolve(result)
        else
            reject(result)
        end
    elseif err then
        reject(err)
    elseif status == "canceled" then
        reject(status)
    end
    t:cancel(0)
end

function requestRunner()
    return effil.thread(function(u, a)
        local https = require "ssl.https"
        local ok, result = pcall(https.request, u, a)
        if ok then
            return {true, result}
        else
            return {false, result}
        end
    end)
end

function async_http_request(url, args, resolve, reject)
    local runner = requestRunner()
    if not reject then
        reject = function()
        end
    end
    newTask(function()
        threadHandle(runner, url, args, resolve, reject)
    end)
end

function encodeUrl(str)
    str = str:gsub(" ", "%+")
    str = str:gsub("\n", "%%0A")
    return u8:encode(str, "CP1251")
end

function sendTG(msg)
    local currentTime = os.time()
    msg = msg:gsub("{......}", "")
    msg = encodeUrl(msg)
    if msg ~= lastMessage or (currentTime - lastMessageTime) > messageCooldown then
        async_http_request("https://api.telegram.org/bot" .. token .. "/sendMessage?chat_id=" .. chatid .. "&text=" .. msg, "", function(result) end)
        lastMessage = msg
        lastMessageTime = currentTime
    end
end

function get_telegram_updates()
    newTask(function()
        while not updateid do
            wait(1)
        end
        local runner = requestRunner()
        local reject = function()
        end
        local args = ""
        while true do
            url = "https://api.telegram.org/bot" .. token .. "/getUpdates?chat_id=" .. chatid .. "&offset=-1"
            threadHandle(runner, url, args, processing_telegram_messages, reject)
            wait(0)
        end
    end)
end

--#meowprd - proxy
function loadProxyList()
	local file = getPath("settings\\farm_proxy.txt")

	if not fileExists(file) then
		local f = io.open(file, "w")
		if f then f:close() print("Created empty farm_proxy.txt") 
		else print("Error create empty farm_proxy.txt") print(select(2, io.open(file, "w"))) return {}
		end
	end

	local f = io.open(file, "r")
	if f then
		local list = {}
		for line in f:lines() do
			if line:match("^(.*) %/ (.*) %/ (.*)$") then
				local ip, user, pass = line:match("(.*) %/ (.*) %/ (.*)")
				if ip then table.insert(list, { ip = ip, user = user or nil, pass = pass or nil }) end
			end
		end
		return list
	else
		print("Error open farm_proxy.txt")
		print(select(2, io.open(file, "r")))
		return {}
	end
	return {}
end
function getRandomProxy()
	local proxyList = loadProxyList()
	if #proxyList == 0 then print("Не найдено ни одного прокси!") print("Пожалуйста, добавьте прокси в файле settings/farm_proxy.txt") PROXY_STATE = true return nil end
	::back_rand_label::
	if #usedProxy == #proxyList then print("Закончились прокси!") return nil end
	math.randomseed(os.clock())
	local rand = math.random(1, #proxyList)
	for k, _ in ipairs(usedProxy) do if k == rand then goto back_rand_label end end
	table.insert(usedProxy, rand)
	return proxyList[rand]
end

function connectRandomProxyFromList()
	local randProxy = getRandomProxy()
	if not randProxy then return end
	print(string.format("Подключаемся к прокси %s", randProxy.ip))
	proxyConnect(randProxy.ip, randProxy.user, randProxy.pass)
end

function onProxyError()
	connectRandomProxyFromList()
end

function onProxyConnect()
	PROXY_STATE = true
    print("Успешно подключились к прокси!")
end

function getLastUpdate()
    local offset = -1  
    async_http_request("https://api.telegram.org/bot" .. token .. "/getUpdates?chat_id=" .. chatid .. "&offset=" .. offset, "", function(result)
        if result then
            local proc_table = json.decode(result)
            if proc_table.ok then
                if #proc_table.result > 0 then
                    local res_table = proc_table.result[1]
                    if res_table then
                        updateid = res_table.update_id
                    end
                else
                    updateid = offset + 1
                end
            end
        end
    end)
end