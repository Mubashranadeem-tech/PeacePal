
import os
import joblib
import numpy as np
from groq import Groq

# --- 1. CONFIGURATION ---
# Set the API Key you provided


# Initialize Groq Client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# --- 2. HELPER FUNCTIONS ---
def normalize(value, min_val, max_val):
    """Converts a real number to a 0.0 - 1.0 scale"""
    norm = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, norm))

def get_svm_prediction(features):
    """Loads the trained model and predicts depression risk"""
    try:
        model = joblib.load('svm_model.pkl')
        # Reshape for a single sample prediction
        data_array = np.array(features).reshape(1, -1)
        prediction = model.predict(data_array)[0]
        return prediction
    except FileNotFoundError:
        print("Error: 'svm_model.pkl' not found. Run train_model.py first!")
        return 0

def get_groq_advice(risk_label, user_text, age_input, stress_input):
    """Sends user data to Groq (Llama 3) for personalized advice"""
    
    system_prompt = """
    You are a professional and empathetic mental health assistant.
    Your task is to analyze the user's health data and personal statement.
    Based on this, provide a response with exactly these three sections:
    1. Motivation (Warm, encouraging words)
    2. Physical Activity (Specific exercises suitable for their age and stress level)
    3. Nutritional Advice (Foods to boost mood and energy)
    Keep the advice practical and concise.  and up to one line max  gave the solution as the user enter its problem and do not talk except health

    """

    user_prompt = f"""
    User Data:
    - Age: {age_input}
    - Reported Stress Level (0-1): {stress_input}
    - Clinical Risk Prediction: {risk_label}
    
    User's Personal Statement: "{user_text}"
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=600, # Increased to allow full advice
        temperature=0.7
    )

    return chat_completion.choices[0].message.content

# --- 3. MAIN APP LOOP ---
def main():
    print("\n" + "="*50)
    print("      MENTAL HEALTH AI AGENT (Powered by Groq)      ")
    print("="*50)

    try:
        # --- INPUT COLLECTION (Human Friendly) ---
        print("\n--- Please answer a few health questions ---")
        
        # Gender
        g_input = input("Gender (Male/Female): ").lower()
        gender = 1.0 if 'male' in g_input else 0.0

        # Age
        age_input = float(input("Age (e.g., 25): "))
        age = normalize(age_input, 18, 60)

        # Sleep
        sleep_input = float(input("Sleep Quality (1-10): "))
        sleep = normalize(sleep_input, 1, 10)

        # Heart Rate
        hr_input = input("Heart Rate (Normal/High/Low): ").lower()
        if 'high' in hr_input: heart_rate = 0.75
        elif 'low' in hr_input: heart_rate = 0.25
        else: heart_rate = 0.50

        # Physical Activity
        pa_input = input("Physical Activity (Low/Moderate/High): ").lower()
        if 'high' in pa_input: activity = 0.8
        elif 'moderate' in pa_input: activity = 0.5
        else: activity = 0.2

        # Caffeine
        caff_input = input("Caffeine Consumption (Low/Moderate/High): ").lower()
        if 'high' in caff_input: caffeine = 0.8
        elif 'moderate' in caff_input: caffeine = 0.5
        else: caffeine = 0.2

        # Alcohol
        alc_input = input("Alcohol Consumption (Low/Moderate/High): ").lower()
        if 'high' in alc_input: alcohol = 0.8
        elif 'moderate' in alc_input: alcohol = 0.5
        else: alcohol = 0.0

        # Smoking
        smoke_input = input("Do you smoke? (Yes/No): ").lower()
        smoking = 1.0 if 'yes' in smoke_input else 0.0

        # Medical Issues
        med_input = input("Any chronic medical issues? (Yes/No): ").lower()
        medical_issue = 1.0 if 'yes' in med_input else 0.0

        # Screen Time
        screen_input = float(input("Avg Screen Time (Hours/day): "))
        screen_time = normalize(screen_input, 0, 12)

        # Stress
        stress_input = int(input("Current Stress (0 = Low, 1 = High): "))
        stress = float(stress_input)

        # Blood Pressure
        bp_input = input("Blood Pressure (Normal/High/Low): ").lower()
        if 'high' in bp_input: bp_sys, bp_dia = 0.8, 0.8
        elif 'low' in bp_input: bp_sys, bp_dia = 0.2, 0.2
        else: bp_sys, bp_dia = 0.5, 0.5

        # --- PREDICTION ---
        features = [gender, age, sleep, heart_rate, activity, caffeine, 
                    alcohol, smoking, medical_issue, screen_time, stress, bp_sys, bp_dia]
        
        risk_pred = get_svm_prediction(features)
        risk_label = "High Risk of Depression" if risk_pred == 1 else "Low Risk / Healthy"

        print(f"\n[Analysis Result] Based on your biometrics: {risk_label}")

        # --- TEXT ANALYSIS ---
        print("\n" + "-"*50)
        print("Tell me how you are feeling mentally right now.")
        print("(e.g., 'I feel anxious about work' or 'I've been isolating myself')")
        user_text = input(">> ")

        print("\n[AI] Generating your personalized plan...")
        advice = get_groq_advice(risk_label, user_text, age_input, stress_input)

        print("\n" + "="*50)
        print("       YOUR PERSONALIZED PLAN       ")
        print("="*50)
        print(advice)

    except ValueError:
        print("Invalid input. Please enter numbers where requested.")

if __name__ == "__main__":

    main()
