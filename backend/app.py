# AI Animation Generator Backend
# Roblox Studio Plugin Backend - Flask + Groq API

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from groq import Groq

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

R15_BONES = [
    "HumanoidRootPart", "LowerTorso", "UpperTorso", "Head",
    "LeftUpperArm", "LeftLowerArm", "LeftHand",
    "RightUpperArm", "RightLowerArm", "RightHand",
    "LeftUpperLeg", "LeftLowerLeg", "LeftFoot",
    "RightUpperLeg", "RightLowerLeg", "RightFoot"
]

R6_BONES = [
    "HumanoidRootPart", "Torso", "Head",
    "Left Arm", "Right Arm",
    "Left Leg", "Right Leg"
]

def build_system_prompt(rig_type):
    bones = R15_BONES if rig_type == "R15" else R6_BONES
    bones_str = ", ".join(bones)
    return (
        "You are a Roblox animation data generator. Your ONLY job is to output valid JSON animation keyframe data.\n\n"
        "The rig type is: " + rig_type + "\n"
        "Available bones: " + bones_str + "\n\n"
        "You must return ONLY a raw JSON object. No explanations, no markdown, no backticks.\n\n"
        "The JSON format must be exactly:\n"
        "{\n"
        "  \"keyframes\": [\n"
        "    {\n"
        "      \"time\": 0.0,\n"
        "      \"poses\": {\n"
        "        \"BoneName\": {\n"
        "          \"position\": [x, y, z],\n"
        "          \"rotation\": [rx, ry, rz],\n"
        "          \"easingStyle\": \"Linear\",\n"
        "          \"easingDirection\": \"Out\"\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- positions are in studs (small values, max +/- 2 from origin)\n"
        "- rotations are in degrees\n"
        "- easingStyle options: Linear, Constant, Elastic, Cubic, Bounce, Back\n"
        "- easingDirection options: In, Out, InOut\n"
        "- Always include at least 4 keyframes for smooth animation\n"
        "- For looping animations, last keyframe should mirror the first\n"
        "- Only include bones relevant to the animation\n"
        "- For walk/run: legs and arms swing, torso bobs\n"
        "- For jump: legs bend up, torso tilts forward\n"
        "- For idle: subtle breathing with torso and head slight sway\n"
        "- For attack: dominant arm extends forward fast\n"
        "- For dance: exaggerated rhythmic movement of torso and arms\n"
        "- For fall: arms spread, legs hang\n"
        "- For climb: alternating arm/leg reach upward\n"
        "- DO NOT include any text outside the JSON"
    )

@app.route("/generate", methods=["POST"])
def generate_animation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        prompt = data.get("prompt", "").strip()
        rig_type = data.get("rigType", "R15")
        loop = data.get("loop", False)

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        if rig_type not in ["R15", "R6"]:
            rig_type = "R15"

        print("[Request] Prompt: " + prompt + " | Rig: " + rig_type)

        user_message = "Generate a Roblox " + rig_type + " animation for: " + prompt + "\nLoop: " + str(loop) + "\nReturn ONLY the JSON. No other text."

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": build_system_prompt(rig_type)},
                {"role": "user", "content": user_message}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=2048,
        )

        raw_response = chat_completion.choices[0].message.content.strip()
        cleaned = re.sub(r"```json|```", "", raw_response).strip()
        anim_data = json.loads(cleaned)

        if "keyframes" not in anim_data:
            return jsonify({"error": "AI returned invalid structure"}), 500
        if not isinstance(anim_data["keyframes"], list) or len(anim_data["keyframes"]) == 0:
            return jsonify({"error": "AI returned empty keyframes"}), 500

        print("[Success] Generated " + str(len(anim_data["keyframes"])) + " keyframes")
        return jsonify(anim_data)

    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse AI response: " + str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error: " + str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "service": "Roblox AI Animator Backend"})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
