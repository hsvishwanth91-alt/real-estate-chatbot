# 🏠 HomeFind - AI Real Estate Chatbot

A simple full-stack real estate website with an AI-style chatbot, built with
**HTML, CSS, JavaScript, Flask (Python), and MySQL**. Designed as a
beginner-friendly college mini project.

## ✨ Features

- **Home page** with hero search bar and featured property listings
- **Property search** by location, budget, and property type
- **Property listing & detail pages** with images, price, and specs
- **AI chatbot** (rule-based, no external API needed) that:
  - Understands greetings, thanks, and goodbyes
  - Extracts budget (e.g. "under 50 lakh", "below 1 crore") from your message
  - Extracts city/location and property type from your message
  - Queries the MySQL database and recommends matching properties
  - Answers simple FAQs about loans/EMI and required documents
- **Site visit booking form** that saves requests to MySQL
- Clean, responsive UI

## 📂 Project Structure

```
real_estate_chatbot/
│
├── app.py                  # Main Flask application (routes)
├── chatbot.py               # Rule-based AI chatbot logic
├── database.sql              # MySQL schema + sample data
├── requirements.txt           # Python dependencies
├── README.md
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html               # Shared layout (navbar, footer, chat widget)
│   ├── index.html               # Home page
│   ├── properties.html           # Search / listing page
│   ├── property_detail.html       # Single property detail page
│   └── book_visit.html             # Site visit booking form
│
└── static/
    ├── css/style.css           # All styling
    ├── js/main.js               # General site JS (flash message auto-hide)
    ├── js/chatbot.js             # Chat widget frontend logic
    └── images/                    # (optional) local images folder
```

## 🛠️ Requirements

- Python 3.9+
- MySQL Server 8.0+ (MySQL Workbench or CLI)
- pip

## 🚀 Setup Instructions

### 1. Clone / Download the project
Place the `real_estate_chatbot` folder anywhere on your machine.

### 2. Create a virtual environment (recommended)
```bash
cd real_estate_chatbot
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the MySQL database
Make sure MySQL server is running, then run:
```bash
mysql -u root -p < database.sql
```
This creates the `real_estate_db` database, the `properties`, `bookings`,
and `chat_logs` tables, and inserts 12 sample properties across Bangalore,
Mumbai, Pune, Chennai, and Delhi.

> Alternatively, open `database.sql` in **MySQL Workbench** and execute it
> as a script.

### 5. Configure database credentials
Open `app.py` and update the `DB_CONFIG` dictionary near the top with your
own MySQL username and password:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # <-- change this
    "database": "real_estate_db"
}
```

### 6. Run the Flask app
```bash
python app.py
```

The app will start at: **http://127.0.0.1:5000/**

Open that URL in your browser.

## 💬 Trying the Chatbot

Click the chat bubble (💬) in the bottom-right corner and try messages like:

- "Hi"
- "Show me 3BHK apartments in Pune under 80 lakh"
- "What villas are available in Chennai?"
- "Recommend a plot under 50 lakh"
- "How to book a visit?"
- "What documents are required to buy property?"

The chatbot works using **keyword and pattern matching** (no external AI
API required), so it runs completely offline and is easy to explain in a
project viva - just walk through `chatbot.py`.

## 🧩 How It Works (Architecture)

1. **Frontend** (HTML/CSS/JS) renders pages using Flask's Jinja2 templates
   and sends search requests as normal GET forms.
2. **Backend** (Flask, `app.py`) handles routing, talks to MySQL using
   `mysql-connector-python`, and exposes a `/chatbot` POST endpoint used by
   the chat widget via `fetch()`.
3. **Chatbot logic** (`chatbot.py`) parses the user's message with regex and
   keyword rules to detect intent (search, greeting, FAQ, etc.), builds a
   SQL query dynamically based on detected filters, and returns a
   formatted natural-language reply.
4. **Database** (MySQL) stores `properties`, `bookings`, and `chat_logs`.

## 🔧 Extending This Project

Ideas if you want to go further for extra credit:
- Add user authentication (login/signup)
- Replace the rule-based chatbot with a real NLP/ML model or an LLM API
- Add property image uploads via an admin panel
- Add pagination to the properties page
- Add email notifications on booking (using `smtplib` or Flask-Mail)

## ❗ Troubleshooting

- **"Access denied for user" error**: double-check the `password` field in
  `DB_CONFIG` inside `app.py`.
- **"Unknown database 'real_estate_db'"**: make sure you ran
  `database.sql` successfully before starting the app.
- **Port already in use**: stop other apps running on port 5000, or run
  `app.run(debug=True, port=5001)` and visit that port instead.

---
Built as a simple, self-contained mini project - no external AI API keys
required. Enjoy! 🎓
