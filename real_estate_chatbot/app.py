"""
app.py
-------
Main Flask application for the AI Real Estate Chatbot website.

Run with:
    python app.py

Make sure you have:
 1. MySQL running with the database created via database.sql
 2. Updated the DB_CONFIG below with your MySQL username/password
 3. Installed dependencies from requirements.txt
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from chatbot import RealEstateChatbot

app = Flask(__name__)
app.secret_key = "college_mini_project_secret_key"  # needed for flash messages

# -------------------------------------------------------------------
# Database configuration - EDIT THESE VALUES to match your MySQL setup
# -------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # <-- change this
    "database": "real_estate_db"
}


def get_db_connection():
    """Create and return a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# Initialize the chatbot, giving it access to the DB connection function
chatbot = RealEstateChatbot(get_db_connection)


# =====================================================================
# ROUTES
# =====================================================================

@app.route("/")
def home():
    """Home page - shows a hero section and a few featured properties."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM properties WHERE status='Available' ORDER BY created_at DESC LIMIT 6")
        featured = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        featured = []
        flash(f"Database connection error: {e}", "error")

    return render_template("index.html", featured=featured)


@app.route("/properties", methods=["GET"])
def properties():
    """
    Property listing page with search/filter by location and budget.
    Query params: location, max_budget, property_type
    """
    location = request.args.get("location", "").strip()
    max_budget = request.args.get("max_budget", "").strip()
    property_type = request.args.get("property_type", "").strip()

    sql = "SELECT * FROM properties WHERE status = 'Available'"
    params = []

    if location:
        sql += " AND (city LIKE %s OR location LIKE %s)"
        params.extend([f"%{location}%", f"%{location}%"])

    if property_type:
        sql += " AND property_type = %s"
        params.append(property_type)

    if max_budget:
        try:
            sql += " AND price <= %s"
            params.append(float(max_budget))
        except ValueError:
            pass  # ignore invalid budget input

    sql += " ORDER BY price ASC"

    results = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "error")

    return render_template(
        "properties.html",
        properties=results,
        location=location,
        max_budget=max_budget,
        property_type=property_type
    )


@app.route("/property/<int:property_id>")
def property_detail(property_id):
    """Detail page for a single property."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM properties WHERE id = %s", (property_id,))
        prop = cursor.fetchone()
        cursor.close()
        conn.close()
    except Error as e:
        prop = None
        flash(f"Database error: {e}", "error")

    if not prop:
        flash("Property not found.", "error")
        return redirect(url_for("properties"))

    return render_template("property_detail.html", property=prop)


@app.route("/book", methods=["GET", "POST"])
def book_visit():
    """Site visit booking form (GET shows form, POST saves booking)."""
    property_id = request.args.get("property_id", type=int)

    # Fetch list of properties for the dropdown
    all_properties = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, title, city FROM properties WHERE status='Available' ORDER BY title")
        all_properties = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "error")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        visit_date = request.form.get("visit_date", "").strip()
        message = request.form.get("message", "").strip()
        selected_property_id = request.form.get("property_id") or None

        if not (name and email and phone and visit_date):
            flash("Please fill in all required fields.", "error")
            return render_template("book_visit.html", properties=all_properties, selected_id=property_id)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO bookings (property_id, name, email, phone, visit_date, message)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (selected_property_id, name, email, phone, visit_date, message)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Your site visit has been booked successfully! Our team will contact you soon.", "success")
            return redirect(url_for("book_visit"))
        except Error as e:
            flash(f"Could not save booking: {e}", "error")

    return render_template("book_visit.html", properties=all_properties, selected_id=property_id)


@app.route("/chatbot", methods=["POST"])
def chatbot_endpoint():
    """
    AJAX endpoint used by the chat widget (static/js/chatbot.js).
    Accepts JSON: { "message": "..." }
    Returns JSON: { "reply": "..." }
    """
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    reply = chatbot.get_response(user_message)

    # Optionally log the conversation
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_message, bot_response) VALUES (%s, %s)",
            (user_message, reply)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error:
        pass  # logging failure should never break the chat experience

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
