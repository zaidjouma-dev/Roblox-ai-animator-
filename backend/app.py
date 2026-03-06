import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = (
    "You are a Roblox animation generator. "
    "Respond with ONLY valid JSON, no markdown, no extra text, no code blocks. "
    "Return exactly this structure with 4 keyframes: "
    "{\"keyframes\":[{\"time\":0,\"poses\":{\"Torso\":{\"rx\":0,\"ry\":0,\"rz\":0},\"Head\":{\"rx\":0,\"ry\":0,\"rz\":0},\"Left Arm\":{\"rx\":0,\"ry\":0,\"rz\":0},\"Right Arm\":{\"rx\":0,\"ry\":0,\"rz\":0},\"Left Leg\":{\"rx\":0,\"ry\":0,\"rz\":0},\"Right Leg\":{\"rx\":0,\"ry\":0,\"rz\":0}}}]} "
    "rx ry rz are rotation in degrees. Use realistic values. 4 keyframes only."
)

BONES_R6 = ["Torso", "Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"]

def extract_rotation(bone_data):
    if not isinstance(bone_data, dict):
        return [0, 0, 0]
    rx = bone_data.get("rx", bone_data.get("rotation_x", 0))
    ry = bone_data.get("ry", bone_data.get("rotation_y", 0))
    rz = bone_data.get("rz", bone_data.get("rotation_z", 0))
    if rx == 0 and ry == 0 and rz == 0:
        cf = bone_data.get("CFrame", bone_data.get("cframe", {}))
        if isinstance(cf, dict):
            rx = cf.get("rx", cf.get("x", 0))
            ry = cf.get("ry", cf.get("y", 0))
            rz = cf.get("rz", cf.get("z", 0))
        rot = bone_data.get("rotation", bone_data.get("Rotation", {}))
        if isinstance(rot, dict):
            rx = rot.get("x", rot.get("rx", 0))
            ry = rot.get("y", rot.get("ry", 0))
            rz = rot.get("z", rot.get("rz", 0))
        elif isinstance(rot, list) and len(rot) >= 3:
            rx, ry, rz = rot[0], rot[1], rot[2]
    try:
        return [float(rx), float(ry), float(rz)]
    except Exception:
        return [0, 0, 0]

def normalize_keyframes(raw_data):
    keyframes = raw_data.get("keyframes", [])
    result = []
    for kf in keyframes:
        time = float(kf.get("time", 0))
        poses_raw = kf.get("poses", kf.get("pose", kf.get("bones", kf.get("Poses", {}))))
        if not isinstance(poses_raw, dict):
            poses_raw = {}
        normalized_poses = {}
        for bone in BONES_R6:
            bone_data = poses_raw.get(bone, {})
            rot = extract_rotation(bone_data)
            normalized_poses[bone] = {
                "position": [0, 0, 0],
                "rotation": rot
            }
        result.append({"time": time, "poses": normalized_poses})
    return result

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "service": "Roblox AI Animator Backend"})

@app.route("/generate", methods=["POST"])
def generate():
    raw = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        prompt = data.get("prompt", "idle animation")
        rig_type = data.get("rigType", "R6")
        loop = data.get("loop", True)

        logger.info("[Request] Prompt: %s | Rig: %s", prompt, rig_type)

        user_message = "Generate a " + prompt + " animation for a " + rig_type + " rig."

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
            return jsonify({"error": "No keyframes in response"}), 500

        normalized = normalize_keyframes(anim_data)
        logger.info("[Success] Normalized %d keyframes", len(normalized))
        return jsonify({"keyframes": normalized})

    except json.JSONDecodeError as e:
        logger.error("[JSON Error] %s", e)
        return jsonify({"error": "AI returned invalid JSON", "details": str(e)}), 500
    except Exception as e:
        logger.error("[Error] %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
