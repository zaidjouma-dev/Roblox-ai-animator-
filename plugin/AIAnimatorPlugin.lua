-- =============================================
-- AI Animation Generator Plugin for Roblox Studio
-- by Zaid | GitHub: roblox-ai-animator
-- =============================================

local HttpService = game:GetService("HttpService")
local Selection = game:GetService("Selection")
local StudioService = game:GetService("StudioService")

-- ⚠️ CHANGE THIS to your deployed backend URL
local BACKEND_URL = "https://roblox-ai-animator-production.up.railway.app/"

-- =============================================
-- PLUGIN SETUP
-- =============================================
local toolbar = plugin:CreateToolbar("AI Animator")
local toggleButton = toolbar:CreateButton(
	"AI Animator",
	"Open AI Animation Generator",
	"rbxassetid://14978048121"
)

local widgetInfo = DockWidgetPluginGuiInfo.new(
	Enum.InitialDockState.Float,
	false,
	false,
	380,
	520,
	300,
	400
)

local widget = plugin:CreateDockWidgetPluginGui("AIAnimatorWidget", widgetInfo)
widget.Title = "AI Animation Generator"

-- =============================================
-- UI SETUP
-- =============================================
local screenGui = Instance.new("ScreenGui")
screenGui.ResetOnSpawn = false
screenGui.Parent = widget

-- Background
local bg = Instance.new("Frame")
bg.Size = UDim2.new(1, 0, 1, 0)
bg.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
bg.BorderSizePixel = 0
bg.Parent = screenGui

-- Title
local title = Instance.new("TextLabel")
title.Size = UDim2.new(1, 0, 0, 50)
title.Position = UDim2.new(0, 0, 0, 0)
title.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
title.BorderSizePixel = 0
title.Text = "🤖 AI Animation Generator"
title.TextColor3 = Color3.fromRGB(255, 255, 255)
title.TextSize = 16
title.Font = Enum.Font.GothamBold
title.Parent = bg

-- Status indicator
local statusDot = Instance.new("Frame")
statusDot.Size = UDim2.new(0, 10, 0, 10)
statusDot.Position = UDim2.new(0, 12, 0, 20)
statusDot.BackgroundColor3 = Color3.fromRGB(100, 100, 100)
statusDot.BorderSizePixel = 0
local dotCorner = Instance.new("UICorner")
dotCorner.CornerRadius = UDim.new(1, 0)
dotCorner.Parent = statusDot
statusDot.Parent = bg

-- Rig info label
local rigLabel = Instance.new("TextLabel")
rigLabel.Size = UDim2.new(1, -24, 0, 30)
rigLabel.Position = UDim2.new(0, 12, 0, 60)
rigLabel.BackgroundTransparency = 1
rigLabel.Text = "⚠ No rig selected"
rigLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
rigLabel.TextSize = 13
rigLabel.Font = Enum.Font.Gotham
rigLabel.TextXAlignment = Enum.TextXAlignment.Left
rigLabel.Parent = bg

-- Divider
local divider = Instance.new("Frame")
divider.Size = UDim2.new(1, -24, 0, 1)
divider.Position = UDim2.new(0, 12, 0, 100)
divider.BackgroundColor3 = Color3.fromRGB(60, 60, 70)
divider.BorderSizePixel = 0
divider.Parent = bg

-- Prompt label
local promptLabel = Instance.new("TextLabel")
promptLabel.Size = UDim2.new(1, -24, 0, 25)
promptLabel.Position = UDim2.new(0, 12, 0, 112)
promptLabel.BackgroundTransparency = 1
promptLabel.Text = "Describe the animation:"
promptLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
promptLabel.TextSize = 13
promptLabel.Font = Enum.Font.GothamBold
promptLabel.TextXAlignment = Enum.TextXAlignment.Left
promptLabel.Parent = bg

-- Text input box
local inputBox = Instance.new("TextBox")
inputBox.Size = UDim2.new(1, -24, 0, 80)
inputBox.Position = UDim2.new(0, 12, 0, 142)
inputBox.BackgroundColor3 = Color3.fromRGB(45, 45, 55)
inputBox.BorderSizePixel = 0
inputBox.Text = ""
inputBox.PlaceholderText = "e.g. slow walk, ninja run, sword attack, idle breathing..."
inputBox.TextColor3 = Color3.fromRGB(255, 255, 255)
inputBox.PlaceholderColor3 = Color3.fromRGB(100, 100, 120)
inputBox.TextSize = 13
inputBox.Font = Enum.Font.Gotham
inputBox.ClearTextOnFocus = false
inputBox.MultiLine = true
inputBox.TextXAlignment = Enum.TextXAlignment.Left
inputBox.TextYAlignment = Enum.TextYAlignment.Top
local inputCorner = Instance.new("UICorner")
inputCorner.CornerRadius = UDim.new(0, 8)
inputCorner.Parent = inputBox
local inputPad = Instance.new("UIPadding")
inputPad.PaddingLeft = UDim.new(0, 8)
inputPad.PaddingTop = UDim.new(0, 6)
inputPad.Parent = inputBox
inputBox.Parent = bg

-- Quick preset buttons
local presetLabel = Instance.new("TextLabel")
presetLabel.Size = UDim2.new(1, -24, 0, 20)
presetLabel.Position = UDim2.new(0, 12, 0, 232)
presetLabel.BackgroundTransparency = 1
presetLabel.Text = "Quick presets:"
presetLabel.TextColor3 = Color3.fromRGB(150, 150, 170)
presetLabel.TextSize = 12
presetLabel.Font = Enum.Font.Gotham
presetLabel.TextXAlignment = Enum.TextXAlignment.Left
presetLabel.Parent = bg

local presets = {"Walk", "Run", "Jump", "Idle", "Attack", "Fall", "Dance", "Climb"}
local presetRow = Instance.new("Frame")
presetRow.Size = UDim2.new(1, -24, 0, 60)
presetRow.Position = UDim2.new(0, 12, 0, 255)
presetRow.BackgroundTransparency = 1
presetRow.Parent = bg

local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 78, 0, 24)
gridLayout.CellPadding = UDim2.new(0, 5, 0, 5)
gridLayout.Parent = presetRow

for _, preset in ipairs(presets) do
	local btn = Instance.new("TextButton")
	btn.BackgroundColor3 = Color3.fromRGB(55, 55, 70)
	btn.BorderSizePixel = 0
	btn.Text = preset
	btn.TextColor3 = Color3.fromRGB(200, 200, 255)
	btn.TextSize = 11
	btn.Font = Enum.Font.Gotham
	local btnCorner = Instance.new("UICorner")
	btnCorner.CornerRadius = UDim.new(0, 6)
	btnCorner.Parent = btn
	btn.Parent = presetRow

	btn.MouseButton1Click:Connect(function()
		inputBox.Text = preset .. " animation"
	end)
end

-- Loop checkbox area
local loopFrame = Instance.new("Frame")
loopFrame.Size = UDim2.new(1, -24, 0, 30)
loopFrame.Position = UDim2.new(0, 12, 0, 328)
loopFrame.BackgroundTransparency = 1
loopFrame.Parent = bg

local loopEnabled = false
local loopCheckbox = Instance.new("TextButton")
loopCheckbox.Size = UDim2.new(0, 20, 0, 20)
loopCheckbox.Position = UDim2.new(0, 0, 0, 5)
loopCheckbox.BackgroundColor3 = Color3.fromRGB(55, 55, 70)
loopCheckbox.BorderSizePixel = 0
loopCheckbox.Text = ""
local cbCorner = Instance.new("UICorner")
cbCorner.CornerRadius = UDim.new(0, 4)
cbCorner.Parent = loopCheckbox
loopCheckbox.Parent = loopFrame

local checkMark = Instance.new("TextLabel")
checkMark.Size = UDim2.new(1, 0, 1, 0)
checkMark.BackgroundTransparency = 1
checkMark.Text = ""
checkMark.TextColor3 = Color3.fromRGB(100, 200, 100)
checkMark.TextSize = 14
checkMark.Font = Enum.Font.GothamBold
checkMark.Parent = loopCheckbox

local loopLabel2 = Instance.new("TextLabel")
loopLabel2.Size = UDim2.new(0, 200, 0, 20)
loopLabel2.Position = UDim2.new(0, 28, 0, 5)
loopLabel2.BackgroundTransparency = 1
loopLabel2.Text = "Loop animation"
loopLabel2.TextColor3 = Color3.fromRGB(180, 180, 200)
loopLabel2.TextSize = 13
loopLabel2.Font = Enum.Font.Gotham
loopLabel2.TextXAlignment = Enum.TextXAlignment.Left
loopLabel2.Parent = loopFrame

loopCheckbox.MouseButton1Click:Connect(function()
	loopEnabled = not loopEnabled
	checkMark.Text = loopEnabled and "✓" or ""
	loopCheckbox.BackgroundColor3 = loopEnabled
		and Color3.fromRGB(60, 120, 60)
		or Color3.fromRGB(55, 55, 70)
end)

-- Generate button
local generateBtn = Instance.new("TextButton")
generateBtn.Size = UDim2.new(1, -24, 0, 44)
generateBtn.Position = UDim2.new(0, 12, 0, 368)
generateBtn.BackgroundColor3 = Color3.fromRGB(80, 120, 255)
generateBtn.BorderSizePixel = 0
generateBtn.Text = "✨ Generate Animation"
generateBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
generateBtn.TextSize = 15
generateBtn.Font = Enum.Font.GothamBold
local genCorner = Instance.new("UICorner")
genCorner.CornerRadius = UDim.new(0, 10)
genCorner.Parent = generateBtn
generateBtn.Parent = bg

-- Status label
local statusLabel = Instance.new("TextLabel")
statusLabel.Size = UDim2.new(1, -24, 0, 40)
statusLabel.Position = UDim2.new(0, 12, 0, 422)
statusLabel.BackgroundTransparency = 1
statusLabel.Text = "Ready. Select a rig to begin."
statusLabel.TextColor3 = Color3.fromRGB(140, 140, 160)
statusLabel.TextSize = 12
statusLabel.Font = Enum.Font.Gotham
statusLabel.TextWrapped = true
statusLabel.TextXAlignment = Enum.TextXAlignment.Left
statusLabel.Parent = bg

-- =============================================
-- HELPER FUNCTIONS
-- =============================================

local function setStatus(msg, color)
	statusLabel.Text = msg
	statusLabel.TextColor3 = color or Color3.fromRGB(140, 140, 160)
end

local function setGenerating(active)
	if active then
		generateBtn.BackgroundColor3 = Color3.fromRGB(60, 60, 80)
		generateBtn.Text = "⏳ Generating..."
		generateBtn.Active = false
	else
		generateBtn.BackgroundColor3 = Color3.fromRGB(80, 120, 255)
		generateBtn.Text = "✨ Generate Animation"
		generateBtn.Active = true
	end
end

-- Detect rig type (R6 or R15)
local function detectRigType(model)
	local humanoid = model:FindFirstChildOfClass("Humanoid")
	if not humanoid then return nil end

	if humanoid.RigType == Enum.HumanoidRigType.R15 then
		return "R15"
	else
		return "R6"
	end
end

-- Get selected rig from selection
local function getSelectedRig()
	local selected = Selection:Get()
	for _, obj in ipairs(selected) do
		if obj:IsA("Model") then
			local humanoid = obj:FindFirstChildOfClass("Humanoid")
			if humanoid then
				return obj
			end
		end
	end
	return nil
end

-- Apply keyframe data to AnimationClip in Animator
local function applyAnimationToRig(rig, animData, prompt)
	local animationController = rig:FindFirstChildOfClass("AnimationController")
		or rig:FindFirstChildOfClass("Humanoid")

	if not animationController then
		setStatus("❌ No AnimationController or Humanoid found!", Color3.fromRGB(255, 80, 80))
		return false
	end

	-- Create a KeyframeSequence
	local keyframeSequence = Instance.new("KeyframeSequence")
	keyframeSequence.Name = "AI_" .. prompt:gsub("%s+", "_"):sub(1, 30)
	keyframeSequence.Loop = loopEnabled
	keyframeSequence.Priority = Enum.AnimationPriority.Action

	-- Parse keyframes from backend response
	for _, kfData in ipairs(animData.keyframes) do
		local keyframe = Instance.new("Keyframe")
		keyframe.Time = kfData.time

		for boneName, poseData in pairs(kfData.poses) do
			local pose = Instance.new("Pose")
			pose.Name = boneName

			local cf = CFrame.new(
				poseData.position[1],
				poseData.position[2],
				poseData.position[3]
			) * CFrame.Angles(
				math.rad(poseData.rotation[1]),
				math.rad(poseData.rotation[2]),
				math.rad(poseData.rotation[3])
			)

			pose.CFrame = cf
			pose.EasingStyle = Enum.PoseEasingStyle[poseData.easingStyle or "Linear"]
			pose.EasingDirection = Enum.PoseEasingDirection[poseData.easingDirection or "Out"]
			pose.Parent = keyframe
		end

		keyframe.Parent = keyframeSequence
	end

	-- Parent to workspace so it shows in AnimationEditor
	keyframeSequence.Parent = game.Workspace
	setStatus("✅ Animation placed in Workspace as: " .. keyframeSequence.Name .. "\n Open Animation Editor → Load → select it!", Color3.fromRGB(100, 220, 100))

	return true
end

-- =============================================
-- SELECTION WATCHER
-- =============================================
Selection.SelectionChanged:Connect(function()
	local rig = getSelectedRig()
	if rig then
		local rigType = detectRigType(rig)
		rigLabel.Text = "✅ Rig: " .. rig.Name .. " (" .. (rigType or "Unknown") .. ")"
		rigLabel.TextColor3 = Color3.fromRGB(100, 220, 100)
		statusDot.BackgroundColor3 = Color3.fromRGB(100, 220, 100)
		setStatus("Ready! Type your animation prompt.", Color3.fromRGB(140, 200, 140))
	else
		rigLabel.Text = "⚠ No rig selected — select a character model"
		rigLabel.TextColor3 = Color3.fromRGB(255, 180, 60)
		statusDot.BackgroundColor3 = Color3.fromRGB(255, 180, 60)
		setStatus("Select a rig with a Humanoid to begin.", Color3.fromRGB(140, 140, 160))
	end
end)

-- =============================================
-- GENERATE BUTTON LOGIC
-- =============================================
generateBtn.MouseButton1Click:Connect(function()
	local rig = getSelectedRig()
	if not rig then
		setStatus("❌ Please select a rig first!", Color3.fromRGB(255, 80, 80))
		return
	end

	local prompt = inputBox.Text
	if prompt == "" or #prompt < 3 then
		setStatus("❌ Please enter an animation description!", Color3.fromRGB(255, 80, 80))
		return
	end

	local rigType = detectRigType(rig)
	if not rigType then
		setStatus("❌ Could not detect rig type (R6/R15).", Color3.fromRGB(255, 80, 80))
		return
	end

	setGenerating(true)
	setStatus("🤖 Contacting AI backend...", Color3.fromRGB(120, 180, 255))

	-- Build request payload
	local payload = HttpService:JSONEncode({
		prompt = prompt,
		rigType = rigType,
		loop = loopEnabled
	})

	local success, result = pcall(function()
		return HttpService:PostAsync(BACKEND_URL, payload, Enum.HttpContentType.ApplicationJson)
	end)

	setGenerating(false)

	if not success then
		setStatus("❌ HTTP Error: " .. tostring(result) .. "\nMake sure your backend is running!", Color3.fromRGB(255, 80, 80))
		return
	end

	local parseSuccess, animData = pcall(function()
		return HttpService:JSONDecode(result)
	end)

	if not parseSuccess or not animData or not animData.keyframes then
		setStatus("❌ Bad response from backend. Check your server logs.", Color3.fromRGB(255, 80, 80))
		return
	end

	applyAnimationToRig(rig, animData, prompt)
end)

-- =============================================
-- TOGGLE WIDGET
-- =============================================
toggleButton.Click:Connect(function()
	widget.Enabled = not widget.Enabled
end)

print("[AI Animator] Plugin loaded successfully! ✅")
