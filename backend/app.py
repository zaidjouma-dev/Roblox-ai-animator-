“””
AI Animation Generator Backend
Roblox Studio Plugin Backend — Flask + Groq API
“””

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from groq import Groq

app = Flask(**name**)
CORS(app)

# Get API key from environment variable

client = Groq(api_key=os.environ.get(“GROQ_API_KEY”))

# =============================================

# RIG BONE DEFINITIONS

# =============================================

R15_BONES = [
“HumanoidRootPart”, “LowerTorso”, “UpperTorso”, “Head”,
“LeftUpperArm”, “LeftLowerArm”, “LeftHand”,
“RightUpperArm”, “RightLowerArm”, “RightHand”,
“LeftUpperLeg”, “LeftLowerLeg”, “LeftFoot”,
“RightUpperLeg”, “RightLowerLeg”, “RightFoot”
]

R6_BONES = [
“HumanoidRootPart”, “Torso”, “Head”,
“Left Arm”, “Right Arm”,
“Left Leg”, “Right Leg”
]

# =============================================

# SYSTEM PROMPT BUILDER

# =============================================

def build_system_prompt(rig_type: str) -> str:
bones = R15_BONES if rig_type == “R15” else R6_BONES
bones_str = “, “.join(bones)

```
return f"""You are a Roblox animation data generator. Your ONLY job is to output valid JSON animation keyframe data.
```

The rig type is: {rig_type}
Available bones: {bones_str}

You must return ONLY a raw JSON object. No explanations, no markdown, no backticks.

The JSON format must be exactly:
{{
“keyframes”: [
{{
“time”: 0.0,
“poses”: {{
“BoneName”: {{
“position”: [x, y, z],
“rotation”: [rx, ry, rz],
“easingStyle”: “Linear”,
“easingDirection”: “Out”
}}
}}
}}
]
}}

Rules:

- positions are in studs (small values, max ±2 from origin)
- rotations are in degrees
- easingStyle options: Linear, Constant, Elastic, Cubic, Bounce, Back
- easingDirection options: In, Out, InOut
- Always include at least 4 keyframes for smooth animation
- For looping animations, last keyframe should mirror the first
- Only include bones relevant to the animation (dont need to include all bones, just the ones that move)
- For walk/run: legs and arms swing, torso bobs
- For jump: legs bend up, torso tilts forward
- For idle: subtle breathing (torso and head slight sway)
- For attack: dominant arm extends forward fast
- For dance: exaggerated rhythmic movement of torso and arms
- For fall: arms spread, legs hang
- For climb: alternating arm/leg reach upward
- Be creative and make realistic-feeling animations
- DO NOT include any text outside the JSON”””

# =============================================

# GENERATION ENDPOINT

# =============================================

@app.route(”/generate”, methods=[“POST”])
def generate_animation():
try:
data = request.get_json()

```
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    prompt = data.get("prompt", "").strip()
    rig_type = data.get("rigType", "R15")
    loop = data.get("loop", False)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if rig_type not in ["R15", "R6"]:
        rig_type = "R15"

    print(f"[Request] Prompt: '{prompt}' | Rig: {rig_type} | Loop: {loop}")

    # Build user message
    user_message = f"""Generate a Roblox {rig_type} animation for: "{prompt}"
```

Loop: {loop}
Return ONLY the JSON. No other text.”””

```
    # Call Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(rig_type)
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        model="llama3-70b-8192",
        temperature=0.7,
        max_tokens=2048,
    )

    raw_response = chat_completion.choices[0].message.content.strip()
    print(f"[Groq Response Raw]: {raw_response[:200]}...")

    # Strip any accidental markdown
    cleaned = re.sub(r"```json|```", "", raw_response).strip()

    # Parse JSON
    anim_data = json.loads(cleaned)

    # Validate structure
    if "keyframes" not in anim_data:
        return jsonify({"error": "AI returned invalid structure (missing 'keyframes')"}), 500

    if not isinstance(anim_data["keyframes"], list) or len(anim_data["keyframes"]) == 0:
        return jsonify({"error": "AI returned empty keyframes list"}), 500

    print(f"[Success] Generated {len(anim_data['keyframes'])} keyframes for '{prompt}'")
    return jsonify(anim_data)

except json.JSONDecodeError as e:
    print(f"[JSON Error]: {e}")
    return jsonify({"error": f"Failed to parse AI response as JSON: {str(e)}"}), 500

except Exception as e:
    print(f"[Server Error]: {e}")
    return jsonify({"error": f"Server error: {str(e)}"}), 500
```

# =============================================

# HEALTH CHECK

# =============================================

@app.route(”/”, methods=[“GET”])
def health():
return jsonify({
“status”: “online”,
“service”: “Roblox AI Animator Backend”,
“version”: “1.0.0”
})

@app.route(”/health”, methods=[“GET”])
def health_check():
return jsonify({“status”: “ok”}), 200

# =============================================

# RUN

# =============================================

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
print(f”[AI Animator Backend] Starting on port {port}”)
app.run(host=“0.0.0.0”, port=port, debug=False)
