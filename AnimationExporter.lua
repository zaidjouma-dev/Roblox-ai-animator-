-- Roblox Default Animation Exporter
-- Put in ServerScriptService and hit Play

local InsertService = game:GetService("InsertService")

-- These are Roblox's OFFICIAL default animation IDs (100% public)
local AnimationIds = {
	{id = "507766666",  name = "Walk"},
	{id = "507767714",  name = "Run"},
	{id = "507765000",  name = "Idle1"},
	{id = "507766388",  name = "Idle2"},
	{id = "507771019",  name = "Jump"},
	{id = "507767337",  name = "Fall"},
	{id = "507768817",  name = "Climb"},
	{id = "507770818",  name = "Swim"},
	{id = "507770677",  name = "SwimIdle"},
	{id = "507776043",  name = "Emote_Wave"},
	{id = "507776814",  name = "Emote_Point"},
	{id = "507777268",  name = "Emote_Dance1"},
	{id = "507776163",  name = "Emote_Laugh"},
	{id = "507775612",  name = "Emote_Cheer"},
}

local R15_TO_R6 = {
	["Torso"]     = {"UpperTorso", "LowerTorso", "Torso"},
	["Head"]      = {"Head"},
	["Left Arm"]  = {"LeftUpperArm", "LeftLowerArm", "LeftHand", "Left Arm"},
	["Right Arm"] = {"RightUpperArm", "RightLowerArm", "RightHand", "Right Arm"},
	["Left Leg"]  = {"LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "Left Leg"},
	["Right Leg"] = {"RightUpperLeg", "RightLowerLeg", "RightFoot", "Right Leg"},
}

local function round(n, d)
	local f = 10^(d or 2)
	return math.floor(n*f+0.5)/f
end

local function cfToAngles(cf)
	local rx,ry,rz = cf:ToEulerAnglesXYZ()
	return round(math.deg(rx)), round(math.deg(ry)), round(math.deg(rz))
end

local function getPoseRot(kf, bone)
	local p = kf:FindFirstChild(bone, true)
	if p and p:IsA("Pose") then
		return cfToAngles(p.CFrame)
	end
	return 0,0,0
end

local function avgRot(kf, bones)
	local sx,sy,sz,c = 0,0,0,0
	for _,b in ipairs(bones) do
		local rx,ry,rz = getPoseRot(kf,b)
		if rx~=0 or ry~=0 or rz~=0 then
			sx=sx+rx; sy=sy+ry; sz=sz+rz; c=c+1
		end
	end
	if c==0 then return 0,0,0 end
	return round(sx/c), round(sy/c), round(sz/c)
end

local function exportAnim(name, kfs)
	local keyframes = kfs:GetKeyframes()
	table.sort(keyframes, function(a,b) return a.Time < b.Time end)
	local max = math.min(#keyframes, 6)
	local step = math.max(1, math.floor(#keyframes/max))
	local selected = {}
	for i=1,#keyframes,step do
		if #selected < max then selected[#selected+1] = keyframes[i] end
	end
	local parts = {}
	for i,kf in ipairs(selected) do
		local poses = {}
		for r6,r15 in pairs(R15_TO_R6) do
			local rx,ry,rz = avgRot(kf, r15)
			poses[#poses+1] = '"'..r6..'":{"rx":'..rx..',"ry":'..ry..',"rz":'..rz..'}'
		end
		local comma = i < #selected and "," or ""
		parts[#parts+1] = '{"time":'..round(kf.Time,2)..',"poses":{'..table.concat(poses,",").."}}"..comma
	end
	return '{"name":"'..name..'","keyframes":['..table.concat(parts,"").."]}"
end

print("=== STARTING === Total: "..#AnimationIds)
local results = {}
local failed = {}

for i,info in ipairs(AnimationIds) do
	print("["..i.."/"..#AnimationIds.."] "..info.name)
	local ok, res = pcall(function()
		local model = InsertService:LoadAsset(tonumber(info.id))
		local kfs = model:FindFirstChildOfClass("KeyframeSequence")
		if not kfs then
			for _,d in ipairs(model:GetDescendants()) do
				if d:IsA("KeyframeSequence") then kfs=d; break end
			end
		end
		if not kfs then error("No KeyframeSequence") end
		local out = exportAnim(info.name, kfs)
		model:Destroy()
		return out
	end)
	if ok and res then
		results[#results+1] = res
		print("OK: "..info.name)
	else
		failed[#failed+1] = info.name
		print("FAILED: "..info.name.." | "..tostring(res))
	end
	task.wait(0.2)
end

print("\n\n=== COPY BELOW ===\n")
print("[")
print(table.concat(results, ",\n"))
print("]")
print("=== COPY ABOVE ===")
print("Success: "..#results.."/"..#AnimationIds)
