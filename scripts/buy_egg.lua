-- Services
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local VirtualUser = game:GetService("VirtualUser")
local RunService = game:GetService("RunService")

-- Configuration
local EGG_NAME = "Bug Egg"
local PURCHASE_EVENT = ReplicatedStorage:WaitForChild("PurchaseEgg", 30)
local PLACE_EVENT = ReplicatedStorage:WaitForChild("PlaceEgg", 30)
local TIMEOUT = 60  -- Max time to wait for actions
local RETRY_ATTEMPTS = 3

-- Anti-AFK
local function prevent_afk()
    VirtualUser:CaptureController()
    VirtualUser:SetKeyDown("w")
    wait(0.1)
    VirtualUser:SetKeyUp("w")
end

-- Purchase egg
local function purchase_egg()
    for attempt = 1, RETRY_ATTEMPTS do
        local success, err = pcall(function()
            PURCHASE_EVENT:FireServer(EGG_NAME)
            wait(2)
            return true
        end)
        if success then
            return true
        end
        warn("Purchase attempt " .. attempt .. " failed: " .. tostring(err))
        wait(1)
    end
    return false
end

-- Place egg
local function place_egg()
    for attempt = 1, RETRY_ATTEMPTS do
        local success, err = pcall(function()
            PLACE_EVENT:FireServer(EGG_NAME)
            wait(2)
            return true
        end)
        if success then
            return true
        end
        warn("Place attempt " .. attempt .. " failed: " .. tostring(err))
        wait(1)
    end
    return false
end

-- Main execution
local start_time = tick()
local success = false

while tick() - start_time < TIMEOUT do
    prevent_afk()
    if not PURCHASE_EVENT or not PLACE_EVENT then
        warn("Required events not found")
        break
    end
    if purchase_egg() and place_egg() then
        success = true
        break
    end
    wait(5)
end

if success then
    Players.LocalPlayer:Kick("Task completed successfully")
else
    Players.LocalPlayer:Kick("Failed to complete task")
end
