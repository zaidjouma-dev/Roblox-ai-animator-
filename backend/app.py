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

client = Groq(api_key=os.environ.get(“GROQ_API_KEY”))

ANIMATION_EXAMPLES = [
{“name”:“Idle”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:0,“ry”:0,“rz”:0},“Head”:{“rx”:5,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-5,“ry”:0,“rz”:5},“Right Arm”:{“rx”:-5,“ry”:0,“rz”:-5},“Left Leg”:{“rx”:0,“ry”:0,“rz”:0},“Right Leg”:{“rx”:0,“ry”:0,“rz”:0}}},{“time”:0.5,“poses”:{“Torso”:{“rx”:2,“ry”:0,“rz”:0},“Head”:{“rx”:3,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-3,“ry”:0,“rz”:5},“Right Arm”:{“rx”:-3,“ry”:0,“rz”:-5},“Left Leg”:{“rx”:0,“ry”:0,“rz”:0},“Right Leg”:{“rx”:0,“ry”:0,“rz”:0}}}]},
{“name”:“Walk”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:5,“ry”:0,“rz”:0},“Head”:{“rx”:-5,“ry”:0,“rz”:0},“Left Arm”:{“rx”:30,“ry”:0,“rz”:5},“Right Arm”:{“rx”:-30,“ry”:0,“rz”:-5},“Left Leg”:{“rx”:-30,“ry”:0,“rz”:0},“Right Leg”:{“rx”:30,“ry”:0,“rz”:0}}},{“time”:0.5,“poses”:{“Torso”:{“rx”:5,“ry”:0,“rz”:0},“Head”:{“rx”:-5,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-30,“ry”:0,“rz”:5},“Right Arm”:{“rx”:30,“ry”:0,“rz”:-5},“Left Leg”:{“rx”:30,“ry”:0,“rz”:0},“Right Leg”:{“rx”:-30,“ry”:0,“rz”:0}}}]},
{“name”:“Run”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:15,“ry”:0,“rz”:0},“Head”:{“rx”:-10,“ry”:0,“rz”:0},“Left Arm”:{“rx”:60,“ry”:0,“rz”:10},“Right Arm”:{“rx”:-60,“ry”:0,“rz”:-10},“Left Leg”:{“rx”:-60,“ry”:0,“rz”:0},“Right Leg”:{“rx”:60,“ry”:0,“rz”:0}}},{“time”:0.3,“poses”:{“Torso”:{“rx”:15,“ry”:0,“rz”:0},“Head”:{“rx”:-10,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-60,“ry”:0,“rz”:10},“Right Arm”:{“rx”:60,“ry”:0,“rz”:-10},“Left Leg”:{“rx”:60,“ry”:0,“rz”:0},“Right Leg”:{“rx”:-60,“ry”:0,“rz”:0}}}]},
{“name”:“Jump”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:-10,“ry”:0,“rz”:0},“Head”:{“rx”:5,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-20,“ry”:0,“rz”:20},“Right Arm”:{“rx”:-20,“ry”:0,“rz”:-20},“Left Leg”:{“rx”:-20,“ry”:0,“rz”:0},“Right Leg”:{“rx”:-20,“ry”:0,“rz”:0}}},{“time”:0.3,“poses”:{“Torso”:{“rx”:5,“ry”:0,“rz”:0},“Head”:{“rx”:-5,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-60,“ry”:0,“rz”:30},“Right Arm”:{“rx”:-60,“ry”:0,“rz”:-30},“Left Leg”:{“rx”:20,“ry”:0,“rz”:0},“Right Leg”:{“rx”:20,“ry”:0,“rz”:0}}}]},
{“name”:“Fall”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:-5,“ry”:0,“rz”:0},“Head”:{“rx”:10,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-30,“ry”:0,“rz”:40},“Right Arm”:{“rx”:-30,“ry”:0,“rz”:-40},“Left Leg”:{“rx”:10,“ry”:0,“rz”:5},“Right Leg”:{“rx”:10,“ry”:0,“rz”:-5}}}]},
{“name”:“Crouch”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:20,“ry”:0,“rz”:0},“Head”:{“rx”:-15,“ry”:0,“rz”:0},“Left Arm”:{“rx”:10,“ry”:0,“rz”:15},“Right Arm”:{“rx”:10,“ry”:0,“rz”:-15},“Left Leg”:{“rx”:-60,“ry”:0,“rz”:5},“Right Leg”:{“rx”:-60,“ry”:0,“rz”:-5}}}]},
{“name”:“Slide”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:40,“ry”:0,“rz”:0},“Head”:{“rx”:-30,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-20,“ry”:0,“rz”:20},“Right Arm”:{“rx”:-20,“ry”:0,“rz”:-20},“Left Leg”:{“rx”:-10,“ry”:0,“rz”:0},“Right Leg”:{“rx”:-80,“ry”:0,“rz”:0}}}]},
{“name”:“Swim”,“keyframes”:[{“time”:0,“poses”:{“Torso”:{“rx”:-80,“ry”:0,“rz”:0},“Head”:{“rx”:70,“ry”:0,“rz”:0},“Left Arm”:{“rx”:160,“ry”:0,“rz”:10},“Right Arm”:{“rx”:-20,“ry”:0,“rz”:-10},“Left Leg”:{“rx”:-10,“ry”:0,“rz”:0},“Right Leg”:{“rx”:10,“ry”:0,“rz”:0}}},{“time”:0.4,“poses”:{“Torso”:{“rx”:-80,“ry”:0,“rz”:0},“Head”:{“rx”:70,“ry”:0,“rz”:0},“Left Arm”:{“rx”:-20,“ry”:0,“rz”:10},“Right Arm”:{“rx”:160,“ry”:0,“rz”:-10},“Left Leg”:{“rx”:10,“ry”:0,“rz”:0},“Right Leg”:{“rx”:-10,“ry”:0,“rz”:0}}}]}
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
example_str = “ Here are reference animations: “
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
