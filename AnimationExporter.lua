-- AI Animation Exporter
-- Run this in Roblox Studio Command Bar or as a Script

local InsertService = game:GetService("InsertService")

local AnimationIds = {
	-- Original set
	{id = "131650813068362", name = "LowCortisol_Dance_R15"},
	{id = "84430246447182",  name = "CaliforniaGirls_Dance_R6"},
	{id = "139440238690196", name = "Aura_Walk_R15"},
	{id = "83860986564910",  name = "Zombie_Walk_R15"},
	{id = "89239655365002",  name = "Idle_Thinker_R6"},
	{id = "110208399858856", name = "Run_R15"},
	{id = "127218870310277", name = "Jordan_Jump_R15"},
	-- New set
	{id = "125091902325921", name = "Idle"},
	{id = "130168917003782", name = "Walk"},
	{id = "82582448610600",  name = "WalkEndLeft"},
	{id = "124055519291233", name = "WalkEndRight"},
	{id = "104922648424294", name = "Run"},
	{id = "79016229148274",  name = "RunEndLeft"},
	{id = "123657303658500", name = "RunEndRight"},
	{id = "139480824858443", name = "RunLowHP"},
	{id = "117883776840806", name = "WalkLowHP"},
	{id = "76980942413814",  name = "Jump"},
	{id = "107736690005007", name = "JumpLeft"},
	{id = "108648402097411", name = "JumpRight"},
	{id = "135537432493704", name = "Fall"},
	{id = "134621252907840", name = "FallLeft"},
	{id = "90188386109450",  name = "FallRight"},
	{id = "76041683869971",  name = "Land"},
	{id = "93378529608964",  name = "Swim"},
	{id = "81246172501995",  name = "Crouch"},
	{id = "109005082967184", name = "Vault"},
	{id = "94185499888794",  name = "WallRunR"},
	{id = "126044262459356", name = "WallRunL"},
	{id = "77451966453920",  name = "Slide"},
	{id = "108210821370435", name = "Roll"},
	{id = "94164580398436",  name = "OpenDoorLeft"},
	{id = "93858736121305",  name = "OpenDoorRight"},
	{id = "137615356964610", name = "JumpOver"},
	{id = "127767979570151", name = "Hold"},
	{id = "101722262147393", name = "BreakLeft"},
	{id = "113381090192164", name = "BreakRight"},
	{id = "113551154921621", name = "PruneIdle"},
	{id = "99074979652803",  name = "PruneMove"},
}

local R15_TO_R6 = {
	["Torso"]     = {"UpperTorso", "LowerTorso", "Torso"},
	["Head"]      = {"Head"},
	["Left Arm"]  = {"LeftUpperArm", "LeftLowerArm", "LeftHand", "Left Arm"},
	["Right Arm"] = {"RightUpperArm", "RightLowerArm", "RightHand", "Right Arm"},
	["Left Leg"]  = {"LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "Left Leg"},
	["Right Leg"] = {"RightUpperLeg", "RightLowerLeg", "RightFoot", "Right Leg"},
}

local function round(n, decimals)
	local factor = 10 ^ (decimals or 2)
	return math.floor(n * factor + 0.5) / factor
end

local function cfToAngles(cf)
	local rx, ry, rz = cf:ToEulerAnglesXYZ()
	return round(math.deg(rx)), round(math.deg(ry)), round(math.deg(rz))
end

local function getPoseRotation(keyframe, boneName)
	local pose = keyframe:FindFirstChild(boneName, true)
	if pose and pose:IsA("Pose") then
		local rx, ry, rz = cfToAngles(pose.CFrame)
		return rx, ry, rz
	end
	return 0, 0, 0
end

local function averageRotations(keyframe, boneList)
	local sumX, sumY, sumZ, count = 0, 0, 0, 0
	for _, boneName in ipairs(boneList) do
		local rx, ry, rz = getPoseRotation(keyframe, boneName)
		if rx ~= 0 or ry ~= 0 or rz ~= 0 then
			sumX = sumX + rx
			sumY = sumY + ry
			sumZ = sumZ + rz
			count = count + 1
		end
	end
	if count == 0 then return 0, 0, 0 end
	return round(sumX/count), round(sumY/count), round(sumZ/count)
end

local function exportAnimation(animName, keyframeSequence)
	local keyframes = keyframeSequence:GetKeyframes()
	table.sort(keyframes, function(a, b) return a.Time < b.Time end)

	-- limit to 6 keyframes max to keep it concise
	local maxKF = math.min(#keyframes, 6)
	local step = math.max(1, math.floor(#keyframes / maxKF))
	local selectedKFs = {}
	for i = 1, #keyframes, step do
		if #selectedKFs < maxKF then
			selectedKFs[#selectedKFs+1] = keyframes[i]
		end
	end

	local kfStrings = {}
	for i, keyframe in ipairs(selectedKFs) do
		local poseEntries = {}
		for r6Bone, r15Bones in pairs(R15_TO_R6) do
			local rx, ry, rz = averageRotations(keyframe, r15Bones)
			poseEntries[#poseEntries+1] = '"' .. r6Bone .. '":{"rx":' .. rx .. ',"ry":' .. ry .. ',"rz":' .. rz .. '}'
		end
		local comma = i < #selectedKFs and "," or ""
		kfStrings[#kfStrings+1] = '{"time":' .. round(keyframe.Time, 2) .. ',"poses":{' .. table.concat(poseEntries, ",") .. '}}' .. comma
	end

	return '{"name":"' .. animName .. '","keyframes":[' .. table.concat(kfStrings, "") .. ']}'
end

-- MAIN
print("=== ANIMATION EXPORTER STARTING === Total: " .. #AnimationIds)
local results = {}
local failed = {}

for i, animInfo in ipairs(AnimationIds) do
	print("[" .. i .. "/" .. #AnimationIds .. "] Loading: " .. animInfo.name)
	local success, result = pcall(function()
		local model = InsertService:LoadAsset(tonumber(animInfo.id))
		if not model then error("LoadAsset returned nil") end
		local kfs = model:FindFirstChildOfClass("KeyframeSequence")
		if not kfs then
			for _, child in ipairs(model:GetDescendants()) do
				if child:IsA("KeyframeSequence") then kfs = child break end
			end
		end
		if not kfs then error("No KeyframeSequence found") end
		local exported = exportAnimation(animInfo.name, kfs)
		model:Destroy()
		return exported
	end)

	if success and result then
		results[#results+1] = result
		print("OK: " .. animInfo.name)
	else
		failed[#failed+1] = animInfo.name
		print("FAILED: " .. animInfo.name .. " | " .. tostring(result))
	end
	task.wait(0.3)
end

print("\n\n=== COPY EVERYTHING BELOW THIS LINE ===\n")
print("[")
print(table.concat(results, ",\n"))
print("]")
print("\n=== COPY EVERYTHING ABOVE THIS LINE ===")
print("Failed: " .. table.concat(failed, ", "))
print("Success: " .. #results .. "/" .. #AnimationIds)
