


# 🍲 AI Recipe Recommender

The backend of the AI-powered recipe recommender app.  
Built with **Flask**, **MySQL**, and **Groq API** to generate and store recipes based on selected ingredients.

---

## ✨ Features
- Generate recipes based on ingredients.
- Store generated recipes in MySQL.
- Integrates with the Groq API for AI-powered recipe suggestions.
---

## 🛠️ Tech Stack
- **Backend:** Flask (Python)
- **Database:** MySQL
- **AI API:** Groq API

---
```
## 📂 Project Structure
backend/
├── app.py # Flask backend
├── config.py # DB + API configuration
├── requirements.txt # Python dependencies
├── .env # Environment variables (not uploaded to GitHub)
├── venv/ # Python virtual environment (not uploaded to GitHub)
└── database/
└── schema.sql # MySQL schema (tables and setup)
├── .gitignore           # Files/folders to ignore in Git
└── README.md            # Project documentation


```
---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/plp-backend.git
cd plp-backend

2.Setup Virtual Environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Database Setup

Login to MySQL and run:

CREATE DATABASE recipe_db;
USE recipe_db;
SOURCE database/schema.sql;

4. Configure Environment Variables

Create a .env file inside backend/:

MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=recipe_db
GROQ_API_KEY=your_groq_api_key


⚠️ Important: Do not upload .env to GitHub.

5. Run the Backend

flask run


Backend will start at http://127.0.0.1:5000/


```

---


```
⚠️ Notes

If someone does not have MySQL installed, they cannot use the database features.
👉 In that case, they can either:

Install MySQL and run schema.sql, OR

Modify the backend to use SQLite (simpler, no external DB setup).

The .env file must be created manually by anyone using this project.

The venv/ (Python virtual environment) should not be uploaded to GitHub.

The __pycache__/ and any .DS_Store files should also be ignored.
```

📝 License

MIT License