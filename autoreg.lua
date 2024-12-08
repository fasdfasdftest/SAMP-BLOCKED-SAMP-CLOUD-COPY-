require('addon')
local sampev = require('samp.events')

function sampev.onShowTextDraw(id, data)
    if data.selectable and data.text == 'selecticon2' and data.position.x == 396.0 and data.position.y == 315.0 then
        for i = 1, math.random(1, 10) do newTask(sendClickTextdraw, i * 500, id) end
    elseif data.selectable and data.text == 'selecticon3' and data.position.x == 233.0 and data.position.y == 337.0 then
        newTask(sendClickTextdraw, 6000, id)
    end
end