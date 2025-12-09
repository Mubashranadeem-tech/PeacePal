
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import os
from groq import Groq

# Change: Tell Flask to look in the current folder for files
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)
os.environ["GROQ_API_KEY"] = "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"
# ... (Keep your API KEY and Model loading code here) ...

# NEW: Route to show your website
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ... (Keep your existing /predict function here) ...
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import joblib
# import numpy as np
# import os
# from groq import Groq

# app = Flask(__name__)
# CORS(app)

# --- CONFIGURATION ---

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load Model
try:
    svm_model = joblib.load('svm_model.pkl')
except:
    pass # Silent fail for demo purposes

def normalize(val, min_v, max_v):
    return (float(val) - min_v) / (max_v - min_v) if max_v > min_v else 0

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # 1. RISK PREDICTION (Kept in background for context)
    age = normalize(data.get('age', 25), 18, 60)
    sleep = normalize(data.get('sleep', 5), 0, 10)
    physical = normalize(data.get('physical', 90), 0, 180)
    screen = normalize(data.get('screen', 5), 0, 12)
    stress = normalize(data.get('stress', 2), 1, 3)
    smoking = 1.0 if data.get('smoking') == "Yes" else 0.0
    
    features = [0.5, age, sleep, 0.5, physical, 0.5, 0.0, smoking, 0.0, screen, stress, 0.5, 0.5]

    try:
        prediction = svm_model.predict(np.array(features).reshape(1, -1))[0]
        risk_label = "High Risk" if prediction == 1 else "Low Risk"
    except:
        risk_label = "Unknown"

    # 2. GENERATE CONVERSATIONAL RESPONSE
    try:
        system_prompt = """
        You are a warm, empathetic, and human-like mental health companion (MindCare).
        
        GOAL:
        Have a natural conversation. Do NOT use bullet points or lists. Do NOT sound like a robot.
        
        INSTRUCTIONS:
        1. IF USER IS HAPPY: 
           - Match their energy! Celebrate with them.
           - Mention a Quranic verse about "Gratitude" (Shukr) naturally in the sentence.
           - Suggest a fun healthy habit (like "Maybe celebrate with a fresh smoothie?").
           - Ask what made their day special.
           
        2. IF USER IS SAD/STRESSED:
           - Validate their feelings first (e.g., "I'm so sorry you're feeling this way...").
           - Gently weave in ONE tip about food or movement (e.g., "Maybe a short walk would help clear your head?").
           - Mention a Quranic verse about "Ease/Patience" (Sabr) naturally to comfort them.
           - Ask a gentle follow-up question to let them vent.
           -Gave some motivation and nutritional advise in  lines also

        FORMAT:
        - Write 3-4 warm sentences.
        - NO "Motivation:", "Nutrition:" labels. Just talk.
        """
        
        user_prompt = f"""
        Context: The user is at {risk_label} of depression. Stress Level: {data.get('stress')}/3.
        User says: "{data.get('userText')}"
        """
        
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.9, # Higher temperature = More creative/human-like
        )
        ai_response = chat.choices[0].message.content
        
    except Exception as e:
        ai_response = "I'm having a little trouble connecting right now, but I'm here for you. Can you tell me that again?"

    return jsonify({
        "risk": risk_label,
        "advice": ai_response
    })

if __name__ == '__main__':

    app.run(debug=True, port=5000)

