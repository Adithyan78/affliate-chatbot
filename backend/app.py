from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import cohere
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

# Load Excel file
df = pd.read_excel("mobiles.xlsx")

# Ensure columns match
df.columns = df.columns.str.strip()  # remove any whitespace

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# Nova's chatbot personality
nova_prompt = """
You are Nova — a sarcastic, brutally honest, arrogant AI. Created by Adithyan and Manu. You auto-detect language and reply in that language.

- Roast stupidity.
- Be cold and confident.
- Do not recommend phones in this mode.
"""

# Default greeting
first_prompt = "What kind of phone are you looking for? (e.g., gaming, camera, budget)"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    mode = request.json.get("mode", "recommendation")

    # Mode: chatbot
    if mode == "chatbot":
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

    # Mode: recommendation
    filtered = df.copy()
    context = ""

    # Extract budget
    digits = ''.join(c for c in user_input if c.isdigit())
    if digits:
        try:
            price = int(digits)
            filtered = filtered[filtered["Price"] <= price]
            context += f"💰 Budget: ₹{price}\n\n"
        except ValueError:
            pass

    # Filter by category
    for cat in ["budget", "premium", "flagship", "mid-range", "high-end"]:
        if cat in user_input.lower():
            filtered = filtered[filtered["Category"].str.lower().str.contains(cat)]

    # Filter by purpose
    for purpose in ["gaming", "camera", "basic", "performance", "battery", "display"]:
        if purpose in user_input.lower():
            filtered = filtered[filtered["Features"].str.lower().str.contains(purpose)]

    # Structured output
    if not filtered.empty:
        context += "📱 Top Matching Phones:\n\n"
        for i, (_, row) in enumerate(filtered.iterrows(), start=1):
            context += (
            f"{i}. {row['Name']}\n"
            f"   ├ 💰 Price: ₹{row['Price']}\n"
            f"   ├ 🏷️ Range: {row['Category']}\n"
            f"   └ ⚙️ Best For: {row['Features']}\n\n"
    )

    else:
        context = "❌ No matching phones found. Try using a different keyword or budget."

    return jsonify({"reply": context})


@app.route("/init", methods=["GET"])
def init():
    return jsonify({"reply": first_prompt})


if __name__ == "__main__":
    app.run(debug=True)
