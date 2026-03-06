# AI Animation Generator Backend

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

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SYSTEM_PROMPT = “”“You are a Roblox animation generator. Generate keyframe animation data as valid JSON only.
No extra text, no markdown, no code blocks. Just raw JSON.

For R6 rigs use these bone names: HumanoidRootPart, Torso, Head, Left Arm, Right Arm, Left Leg, Right Leg
For R15 rigs use these bone names: HumanoidRootPart, UpperTorso, LowerTorso, Head, LeftUpperArm, LeftLowerArm, LeftHand, RightUpperArm, RightLowerArm, RightHand, LeftUpperLeg, LeftLowerLeg, LeftFoot, RightUpperLeg, RightLowerLeg, RightFoot

Return ONLY this JSON structure:
{
“keyframes”: [
{
“time”: 0,
“poses”: {
“HumanoidRootPart”: {“position”: [0,0,0], “rotation”: [0,0,0], “easingStyle”: “Linear”, “easingDirection”: “Out”},
“Torso”: {“position”: [0,0,0], “rotation”: [0,0,0], “easingStyle”: “Linear”, “easingDirection”: “Out”}
}
}
]
}

Generate 4-6 keyframes for a smooth animation loop. Use realistic rotation values in degrees.”””

@app.route(”/health”, methods=[“GET”])
def health():
return jsonify({“status”: “online”, “service”: “Roblox AI Animator Backend”})

@app.route(”/generate”, methods=[“POST”])
def generate():
try:
data = request.get_json()
if not data:
return jsonify({“error”: “No JSON body”}), 400

```
    prompt = data.get("prompt", "idle animation")
    rig_type = data.get("rigType", "R6")
    loop = data.get("loop", True)

    logger.info(f"[Request] Prompt: {prompt} | Rig: {rig_type}")

    user_message = f"Generate a '{prompt}' animation for a {rig_type} rig. Loop: {loop}."

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        max_tokens=2000,
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()
    logger.info(f"[Groq Response] {raw[:200]}")

    # Strip markdown if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    anim_data = json.loads(raw)

    if "keyframes" not in anim_data:
        return jsonify({"error": "No keyframes in response", "raw": raw}), 500

    logger.info(f"[Success] Generated {len(anim_data['keyframes'])} keyframes")
    return jsonify(anim_data)

except json.JSONDecodeError as e:
    logger.error(f"[JSON Error] {e} | Raw: {raw if 'raw' in locals() else 'N/A'}")
    return jsonify({"error": "AI returned invalid JSON", "details": str(e)}), 500
except Exception as e:
    logger.error(f"[Error] {e}")
    return jsonify({"error": str(e)}), 500
```

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port, debug=False)
