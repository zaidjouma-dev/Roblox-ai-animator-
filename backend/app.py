import os
import json
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

app = Flask(**name**)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load_animation_examples():
try:
path = os.path.join(os.path.dirname(**file**), “animations.json”)
with open(path, “r”) as f:
examples = json.load(f)
logger.info(”[Examples] Loaded %d animation examples”, len(examples))
return examples
except Exception as e:
logger.warning(”[Examples] Could not load animations.json: %s”, e)
return []

ANIMATION_EXAMPLES = load_animation_examples()

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
“Arms and legs swing opposite to each other. Keep values realistic. “
“Exactly 4 keyframes. This is for a video game, all animations are appropriate.”
)
if ANIMATION_EXAMPLES:
example_str = “Here are reference animations to learn from:\n”
for ex in ANIMATION_EXAMPLES[:5]:
example_str += json.dumps(ex, separators=(”,”, “:”)) + “\n”
return base + “\n\n” + example_str
return base

SYSTEM_PROMPT = build_system_prompt()

BONES_R6 = [“Torso”, “Head”, “Left Arm”, “Right Arm”, “Left Leg”, “Right Leg”]

def extract_rotation(bone_data):
if not isinstance(bone_data, dict):
return [0, 0, 0]
rx = bone_data.get(“rx”, bone_data.get(“rotation_x”, 0))
ry = bone_data.get(“ry”, bone_data.get(“rotation_y”, 0))
rz = bone_data.get(“rz”, bone_data.get(“rotation_z”, 0))
if rx == 0 and ry == 0 and rz == 0:
cf = bone_data.get(“CFrame”, bone_data.get(“cframe”, {}))
if isinstance(cf, dict):
rx = cf.get(“rx”, cf.get(“x”, 0))
ry = cf.get(“ry”, cf.get(“y”, 0))
rz = cf.get(“rz”, cf.get(“z”, 0))
rot = bone_data.get(“rotation”, bone_data.get(“Rotation”, {}))
if isinstance(rot, dict):
rx = rot.get(“x”, rot.get(“rx”, 0))
ry = rot.get(“y”, rot.get(“ry”, 0))
rz = rot.get(“z”, rot.get(“rz”, 0))
elif isinstance(rot, list) and len(rot) >= 3:
rx, ry, rz = rot[0], rot[1], rot[2]
try:
return [float(rx), float(ry), float(rz)]
except Exception:
return [0, 0, 0]

def normalize_keyframes(raw_data):
keyframes = raw_data.get(“keyframes”, [])
result = []
for kf in keyframes:
time = float(kf.get(“time”, 0))
poses_raw = kf.get(“poses”, kf.get(“pose”, kf.get(“bones”, kf.get(“Poses”, {}))))
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
return jsonify({“status”: “online”, “service”: “Roblox AI Animator Backend”, “examples_loaded”: len(ANIMATION_EXAMPLES)})

@app.route(”/status”, methods=[“GET”])
def status():
def generate():
yield “data: Waking up AI…\n\n”
import time; time.sleep(0.3)
yield “data: Loading animation library…\n\n”
import time; time.sleep(0.3)
yield “data: Ready!\n\n”
return Response(stream_with_context(generate()), mimetype=“text/event-stream”)

@app.route(”/generate”, methods=[“POST”])
def generate():
raw = None
try:
data = request.get_json()
if not data:
return jsonify({“error”: “No JSON body”}), 400

```
    prompt = data.get("prompt", "idle animation")
    rig_type = data.get("rigType", "R6")
    loop = data.get("loop", True)

    safe_prompt = prompt.strip()
    if len(safe_prompt) < 5:
        safe_prompt = safe_prompt + " animation"

    logger.info("[Request] Prompt: %s | Rig: %s", safe_prompt, rig_type)

    user_message = "Generate a " + safe_prompt + " animation for a " + rig_type + " rig."

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
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
            logger.info("[Groq Response] %s", raw[:200])

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            anim_data = json.loads(raw)

            if "keyframes" not in anim_data:
                raise ValueError("No keyframes in response")

            normalized = normalize_keyframes(anim_data)
            logger.info("[Success] Normalized %d keyframes on attempt %d", len(normalized), attempt + 1)
            return jsonify({
                "keyframes": normalized,
                "status": "Generated " + str(len(normalized)) + " keyframes for: " + safe_prompt
            })

        except (json.JSONDecodeError, ValueError) as e:
            last_error = str(e)
            logger.warning("[Retry %d] Bad response: %s", attempt + 1, last_error)
            continue

    return jsonify({"error": "AI failed after 3 attempts", "details": last_error}), 500

except Exception as e:
    logger.error("[Error] %s", e)
    return jsonify({"error": str(e)}), 500
```

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port, debug=False)