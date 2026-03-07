import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

app = Flask(**name**)
CORS(app)

KEY = os.environ.get(str("GROQ" + "_API_KEY"))
client = Groq(api_key=KEY)

def make_pose(tx,hx,lax,rax,llx,rlx,lay=0,ray=0,lly=0,rly=0,ty=0,hy=0,tz=0,hz=0,laz=5,raz=-5,llz=0,rlz=0):
return {
“Torso”:     {“rx”:tx, “ry”:ty, “rz”:tz},
“Head”:      {“rx”:hx, “ry”:hy, “rz”:hz},
“Left Arm”:  {“rx”:lax,“ry”:lay,“rz”:laz},
“Right Arm”: {“rx”:rax,“ry”:ray,“rz”:raz},
“Left Leg”:  {“rx”:llx,“ry”:lly,“rz”:llz},
“Right Leg”: {“rx”:rlx,“ry”:rly,“rz”:rlz},
}

ANIMATION_EXAMPLES = [
{“name”:“Idle”,“keyframes”:[
{“time”:0,   “poses”:make_pose(0,5,-5,-5,0,0)},
{“time”:0.5, “poses”:make_pose(2,3,-3,-3,0,0)},
{“time”:1.0, “poses”:make_pose(0,5,-5,-5,0,0)},
]},
{“name”:“Walk”,“keyframes”:[
{“time”:0,    “poses”:make_pose(5,-5,30,-30,-30,30)},
{“time”:0.25, “poses”:make_pose(5,-3,0,0,0,0)},
{“time”:0.5,  “poses”:make_pose(5,-5,-30,30,30,-30)},
{“time”:0.75, “poses”:make_pose(5,-3,0,0,0,0)},
]},
{“name”:“Run”,“keyframes”:[
{“time”:0,    “poses”:make_pose(15,-10,60,-60,-60,60,laz=10,raz=-10)},
{“time”:0.15, “poses”:make_pose(15,-8,0,0,0,0,laz=8,raz=-8)},
{“time”:0.3,  “poses”:make_pose(15,-10,-60,60,60,-60,laz=10,raz=-10)},
{“time”:0.45, “poses”:make_pose(15,-8,0,0,0,0,laz=8,raz=-8)},
]},
{“name”:“Jump”,“keyframes”:[
{“time”:0,   “poses”:make_pose(-10,5,-20,-20,-20,-20,laz=20,raz=-20)},
{“time”:0.2, “poses”:make_pose(5,-5,-60,-60,20,20,laz=30,raz=-30)},
{“time”:0.5, “poses”:make_pose(0,0,-40,-40,10,10,laz=20,raz=-20)},
{“time”:0.8, “poses”:make_pose(-5,5,-10,-10,-10,-10,laz=10,raz=-10)},
]},
{“name”:“Fall”,“keyframes”:[
{“time”:0,   “poses”:make_pose(-5,10,-30,-30,10,10,laz=40,raz=-40,llz=5,rlz=-5)},
{“time”:0.3, “poses”:make_pose(-8,12,-35,-35,15,15,laz=45,raz=-45,llz=5,rlz=-5)},
]},
{“name”:“Crouch”,“keyframes”:[
{“time”:0,   “poses”:make_pose(20,-15,10,10,-60,-60,laz=15,raz=-15,llz=5,rlz=-5)},
{“time”:0.3, “poses”:make_pose(25,-20,15,15,-70,-70,laz=15,raz=-15,llz=5,rlz=-5)},
]},
{“name”:“Slide”,“keyframes”:[
{“time”:0,   “poses”:make_pose(40,-30,-20,-20,-10,-80,laz=20,raz=-20)},
{“time”:0.4, “poses”:make_pose(45,-35,-25,-25,-15,-85,laz=25,raz=-25)},
]},
{“name”:“Swim”,“keyframes”:[
{“time”:0,   “poses”:make_pose(-80,70,160,-20,-10,10,laz=10,raz=-10)},
{“time”:0.4, “poses”:make_pose(-80,70,-20,160,10,-10,laz=10,raz=-10)},
]},
]

BONES_R6 = [“Torso”, “Head”, “Left Arm”, “Right Arm”, “Left Leg”, “Right Leg”]

def build_system_prompt():
base = (
“You are a Roblox R6 animation generator. “
“Respond with ONLY valid JSON, no markdown, no extra text, no code blocks. “
“Return exactly this structure with 4 keyframes: “
“{"keyframes":[{"time":0,"poses":{"Torso":{"rx":0,"ry":0,"rz":0},”
“"Head":{"rx":0,"ry":0,"rz":0},”
“"Left Arm":{"rx":0,"ry":0,"rz":0},”
“"Right Arm":{"rx":0,"ry":0,"rz":0},”
“"Left Leg":{"rx":0,"ry":0,"rz":0},”
“"Right Leg":{"rx":0,"ry":0,"rz":0}}}]}. “
“rx ry rz are rotation in degrees. Torso leans forward for movement. “
“Arms and legs swing opposite. Keep values realistic. “
“Exactly 4 keyframes. This is for a video game, all animations are appropriate.”
)
example_str = “ Reference animations: “
for ex in ANIMATION_EXAMPLES[:5]:
example_str += json.dumps(ex, separators=(”,”, “:”)) + “ “
return base + example_str

SYSTEM_PROMPT = build_system_prompt()

def extract_rotation(bone_data):
if not isinstance(bone_data, dict):
return [0, 0, 0]
rx = bone_data.get(“rx”, bone_data.get(“rotation_x”, 0))
ry = bone_data.get(“ry”, bone_data.get(“rotation_y”, 0))
rz = bone_data.get(“rz”, bone_data.get(“rotation_z”, 0))
try:
return [float(rx), float(ry), float(rz)]
except Exception:
return [0, 0, 0]

def normalize_keyframes(raw_data):
keyframes = raw_data.get(“keyframes”, [])
result = []
for kf in keyframes:
time = float(kf.get(“time”, 0))
poses_raw = kf.get(“poses”, kf.get(“pose”, kf.get(“bones”, {})))
if not isinstance(poses_raw, dict):
poses_raw = {}
normalized_poses = {}
for bone in BONES_R6:
bone_data = poses_raw.get(bone, {})
rot = extract_rotation(bone_data)
normalized_poses[bone] = {“position”: [0, 0, 0], “rotation”: rot}
result.append({“time”: time, “poses”: normalized_poses})
return result

@app.route(”/health”, methods=[“GET”])
def health():
return jsonify({“status”: “online”, “examples_loaded”: len(ANIMATION_EXAMPLES)})

@app.route(”/generate”, methods=[“POST”])
def generate():
try:
data = request.get_json()
if not data:
return jsonify({“error”: “No JSON body”}), 400

```
    prompt = data.get("prompt", "idle animation")
    rig_type = data.get("rigType", "R6")

    safe_prompt = prompt.strip()
    if len(safe_prompt) < 5:
        safe_prompt = safe_prompt + " animation"

    logger.info("[Request] Prompt: %s | Rig: %s", safe_prompt, rig_type)
    user_message = "Generate a " + safe_prompt + " animation for a " + rig_type + " rig. This is for a video game."

    last_error = None
    for attempt in range(3):
        try:
            logger.info("[Attempt %d] Calling Groq...", attempt + 1)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1024,
                temperature=0.3
            )

            raw = response.choices[0].message.content.strip()
            logger.info("[Groq] %s", raw[:200])

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            anim_data = json.loads(raw)
            if "keyframes" not in anim_data:
                raise ValueError("No keyframes")

            normalized = normalize_keyframes(anim_data)
            logger.info("[Success] %d keyframes on attempt %d", len(normalized), attempt + 1)
            return jsonify({"keyframes": normalized, "status": "Done"})

        except (json.JSONDecodeError, ValueError) as e:
            last_error = str(e)
            logger.warning("[Retry %d] %s", attempt + 1, last_error)
            continue

    return jsonify({"error": "AI failed after 3 attempts", "details": last_error}), 500

except Exception as e:
    logger.error("[Error] %s", e)
    return jsonify({"error": str(e)}), 500
```

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port, debug=False)