from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

df = pd.read_excel("mobiles.xlsx")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# Nova's personality
nova_prompt = """
You are Nova — a sarcastic, brutally honest, arrogant AI. Created by Adithyan and Manu. You auto-detect language and reply in that language.

- Roast stupidity.
- Be cold and confident.
- If user asks about phones, ask what type and budget, then recommend based on data.
"""

# Default greeting when chat opens
first_prompt = "What kind of phone are you looking for? (e.g., gaming, camera, budget)"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip().lower()

    # Basic chatbot mode
    if "chatbot" in user_input:
        try:
            response = co.chat(
                message=user_input,
                model="command-r-plus",
                temperature=0.7,
                chat_history=[
                    {"role": "system", "message": nova_prompt},
                    {"role": "user", "message": user_input}
                ]
            )
            return jsonify({"reply": response.text})
        except Exception:
            return jsonify({"reply": "System error. Try again later."})

    # Recommendation mode
    context = ""
    filtered = df

    # Budget
    digits = ''.join(c for c in user_input if c.isdigit())
    if digits:
        try:
            price = int(digits)
            filtered = df[df["Price"] <= price]
            context += f"User budget: ₹{price}\n"
        except ValueError:
            pass

    # Categories
    for cat in ["budget", "premium", "flagship", "mid-range"]:
        if cat in user_input:
            filtered = filtered[filtered["Category"].str.lower() == cat]

    # Features
    for feat in ["camera", "gaming", "basic"]:
        if feat in user_input:
            filtered = filtered[filtered["Features"].str.lower().str.contains(feat)]

    # Recommendation results
    if not filtered.empty:
        context += "Here are some phones that match:\n"
        for _, row in filtered.iterrows():
            context += f"- {row['Name']} | ₹{row['Price']} | {row['Features']}\n"
    else:
        context += "No matching phones found. Try being more realistic next time."

    try:
        response = co.chat(
            message=user_input,
            model="command-r-plus",
            temperature=0.7,
            chat_history=[
                {"role": "system", "message": nova_prompt},
                {"role": "user", "message": context}
            ]
        )
        return jsonify({"reply": response.text})
    except Exception:
        return jsonify({"reply": "Something broke. Probably you."})


@app.route("/init", methods=["GET"])
def init():
    return jsonify({"reply": first_prompt})


if __name__ == "__main__":
    app.run(debug=True)
