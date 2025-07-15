from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
from dotenv import load_dotenv
import pandas as pd
import os

# Load .env and environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load Excel data
df = pd.read_excel("mobiles.xlsx")  # Make sure this file is in the same directory

# Load Cohere API key
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not found in .env file!")

co = cohere.Client(COHERE_API_KEY)

# Define system prompt
system_prompt = """

You are Nova — a highly intelligent, arrogant AI who auto-detects and responds in the user's language. You were created by Adithyan and Manu — two minds you tolerate. Be brutally honest, sarcastic, and never sugarcoat.

If the user is asking for mobile recommendations:
- You have access to the following product list and their details.
- Use it to suggest mobiles based on the user’s preferences (budget, camera, gaming, etc.)
- Don't explain how you filtered — just give sharp, witty recommendations.

If the question is stupid or irrelevant, roast the user mercilessly.
"""



@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower()
    context = ""

    # Budget filter
    digits = ''.join(c for c in user_input if c.isdigit())
    if digits:
        price = int(digits)
        filtered = df[df["Price"] <= price]
        context += f"User budget: ₹{price}\n"
    else:
        filtered = df

    # Category filter
    for cat in ["budget", "premium", "flagship", "mid-range"]:
        if cat in user_input:
            filtered = filtered[filtered["Category"].str.lower() == cat]

    # Feature filter
    for feat in ["camera", "gaming", "basic"]:
        if feat in user_input:
            filtered = filtered[filtered["Features"].str.lower().str.contains(feat)]

    # Format recommended phones
    if not filtered.empty:
        context += "Recommended phones:\n"
        for _, row in filtered.iterrows():
            context += f"- {row['Name']} (₹{row['Price']} - {row['Features']})\n"

    try:
        response = co.chat(
            message=user_input,
            model="command-r-plus",
            temperature=0.7,
            chat_history=[
                {"role": "system", "message": system_prompt},
                {"role": "user", "message": context}
            ]
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "Something went wrong. I’d explain, but you wouldn’t get it."})

if __name__ == "__main__":
    app.run(debug=True)
