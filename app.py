# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import requests
import re
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL Config
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Pass@1234"),
    "database": os.getenv("DB_NAME", "recipe_db")
}

# Groq API Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Supported model

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/generate", methods=["POST"])
def generate_recipes():
    data = request.get_json() or {}
    ingredients = data.get("ingredients", [])
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    prompt = (
        f"Suggest 4 simple, affordable recipes using: {', '.join(ingredients)}. "
        "For each recipe, include a title, an ingredients list, and instructions."
    )

    try:
        print("🔹 Sending request to Groq...")
        response = requests.post(GROQ_URL, headers=headers, json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 800
        })

        print("🔹 Groq status:", response.status_code)
        print("🔹 Groq response raw:", response.text[:300])  # preview first 300 chars

        if response.status_code != 200:
            return jsonify({
                "error": f"Groq API error {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()
        print("🔹 Parsed JSON keys:", result.keys())

        content = result["choices"][0]["message"]["content"].strip()

        # --- Smart split logic ---
        parts = re.split(r"(?:\*\*Recipe \d+:|\nRecipe \d+:)", content, flags=re.IGNORECASE)
        recipes = []

        for part in parts:
            text = part.strip()
            if not text:
                continue

            # Use first line as title if available
            lines = text.split("\n", 1)
            title = lines[0][:50]  # limit title to 50 chars
            body = lines[1] if len(lines) > 1 else ""

            recipes.append({
                "title": f"Recipe {len(recipes)+1}: {title}",
                "ingredients": ", ".join(ingredients),
                "instructions": body.strip()
            })

        # Fallback: if nothing parsed, just cut into 2 parts
        if not recipes:
            half = len(content) // 2
            recipes = [
                {"title": "AI Recipe Suggestions (Part 1)", "ingredients": ", ".join(ingredients), "instructions": content[:half]},
                {"title": "AI Recipe Suggestions (Part 2)", "ingredients": ", ".join(ingredients), "instructions": content[half:]}
            ]

        # Save to DB
        print("🔹 Inserting into DB...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipe_logs (ingredients, result_text) VALUES (%s, %s)",
            (", ".join(ingredients), content)
        )
        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Success!")
        return jsonify({"recipes": recipes})

    except Exception as e:
        print("❌ Error in backend:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True )
