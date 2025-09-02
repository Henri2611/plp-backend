# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import requests
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load local .env variables (for local testing)
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- MySQL Config using DATABASE_URL ---
DATABASE_URL = os.environ.get("DATABASE_URL")  # Railway sets this automatically

def get_db_connection():
    try:
        if DATABASE_URL:
            # Parse DATABASE_URL from Railway
            parsed = urlparse(DATABASE_URL)
            return mysql.connector.connect(
                host=parsed.hostname,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:],  # remove leading /
                port=parsed.port or 3306
            )
        else:
            # Fallback to local .env / defaults
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "Pass@1234"),
                database=os.getenv("DB_NAME", "recipe_db"),
                port=int(os.getenv("DB_PORT", 3306))
            )
    except mysql.connector.Error as err:
        print("❌ MySQL connection error:", err)
        raise

# Groq API Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Supported model

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

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

        if response.status_code != 200:
            return jsonify({
                "error": f"Groq API error {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()

        # --- Smart split logic ---
        parts = re.split(r"(?:\*\*Recipe \d+:|\nRecipe \d+:)", content, flags=re.IGNORECASE)
        recipes = []

        for part in parts:
            text = part.strip()
            if not text:
                continue
            lines = text.split("\n", 1)
            title = lines[0][:50]
            body = lines[1] if len(lines) > 1 else ""
            recipes.append({
                "title": f"Recipe {len(recipes)+1}: {title}",
                "ingredients": ", ".join(ingredients),
                "instructions": body.strip()
            })

        if not recipes:
            half = len(content) // 2
            recipes = [
                {"title": "AI Recipe Suggestions (Part 1)", "ingredients": ", ".join(ingredients), "instructions": content[:half]},
                {"title": "AI Recipe Suggestions (Part 2)", "ingredients": ", ".join(ingredients), "instructions": content[half:]}
            ]

        # --- Save to DB ---
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

    except mysql.connector.Error as db_err:
        print("❌ Database error:", db_err)
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        print("❌ Error in backend:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/test-db", methods=["GET"])
def test_db():
    """Test database connection and fetch last 5 rows from recipe_logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ingredients, result_text, created_at FROM recipe_logs ORDER BY id DESC LIMIT 5"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert rows to list of dicts for JSON response
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "ingredients": row[1],
                "result_text": row[2],
                "created_at": str(row[3])
            })

        return {"success": True, "last_5_rows": results}

    except Exception as e:
        return {"success": False, "error": str(e)}, 500


if __name__ == "__main__":
    # Use PORT from Railway if set
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
