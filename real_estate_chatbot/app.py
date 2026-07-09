"""
app.py
-------
Main Flask application for the AI Real Estate Chatbot website.
"""

import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:  # pragma: no cover - optional dependency for local MySQL use
    mysql.connector = None
    MySQLError = Exception

try:
    from .chatbot import RealEstateChatbot
except ImportError:  # pragma: no cover - allows running app.py directly
    from chatbot import RealEstateChatbot

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.secret_key = os.getenv("SECRET_KEY", "college_mini_project_secret_key")


def get_db_connection():
    """Create a database connection that works locally and on Render."""
    if os.getenv("DB_HOST") and os.getenv("DB_NAME") and mysql.connector:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "real_estate_db"),
            autocommit=True,
        )

    db_path = Path(os.getenv("DB_FILE", str(BASE_DIR / "instance" / "real_estate.db")))
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _is_sqlite(conn):
    return isinstance(conn, sqlite3.Connection)


def _normalize_query(query, conn):
    if _is_sqlite(conn):
        return query, tuple()
    return query.replace("?", "%s"), tuple()


def _fetch_all(query, params=()):
    conn = get_db_connection()
    try:
        if _is_sqlite(conn):
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        cursor = conn.cursor(dictionary=True)
        normalized_query = query.replace("?", "%s")
        cursor.execute(normalized_query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def _fetch_one(query, params=()):
    conn = get_db_connection()
    try:
        if _is_sqlite(conn):
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row is not None else None

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query.replace("?", "%s"), params)
        return cursor.fetchone()
    finally:
        conn.close()


def _write(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if _is_sqlite(conn):
            cursor.execute(query, params)
        else:
            cursor.execute(query.replace("?", "%s"), params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def init_db():
    """Create tables and seed sample data when the app starts."""
    conn = get_db_connection()
    try:
        if _is_sqlite(conn):
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    property_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    city TEXT NOT NULL,
                    price REAL NOT NULL,
                    bedrooms INTEGER DEFAULT 0,
                    bathrooms INTEGER DEFAULT 0,
                    area_sqft INTEGER DEFAULT 0,
                    description TEXT,
                    image_url TEXT,
                    status TEXT DEFAULT 'Available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id INTEGER,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    visit_date TEXT NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT,
                    bot_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
            if count == 0:
                conn.executemany(
                    """
                    INSERT INTO properties (
                        title, property_type, location, city, price, bedrooms, bathrooms,
                        area_sqft, description, image_url, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "Sunrise 3BHK Apartment",
                            "Apartment",
                            "Whitefield",
                            "Bangalore",
                            7500000,
                            3,
                            2,
                            1450,
                            "A modern 3BHK apartment with clubhouse, gym, and swimming pool access.",
                            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                            "Available",
                        ),
                        (
                            "Green Valley Villa",
                            "Villa",
                            "Sarjapur Road",
                            "Bangalore",
                            15000000,
                            4,
                            4,
                            3200,
                            "Spacious 4BHK independent villa with private garden and parking for 2 cars.",
                            "https://images.unsplash.com/photo-1568605114967-8130f3a36994",
                            "Available",
                        ),
                        (
                            "Cozy 2BHK Flat",
                            "Apartment",
                            "Andheri West",
                            "Mumbai",
                            9500000,
                            2,
                            2,
                            1050,
                            "Well-ventilated 2BHK flat near the railway station.",
                            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
                            "Available",
                        ),
                        (
                            "Budget 1BHK Studio",
                            "Apartment",
                            "Hinjewadi",
                            "Pune",
                            3200000,
                            1,
                            1,
                            550,
                            "Affordable studio apartment close to IT hubs.",
                            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
                            "Available",
                        ),
                        (
                            "Lakeview 3BHK Apartment",
                            "Apartment",
                            "Powai",
                            "Mumbai",
                            18500000,
                            3,
                            3,
                            1600,
                            "Premium apartment overlooking Powai lake with modern amenities.",
                            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914",
                            "Available",
                        ),
                    ],
                )
            conn.commit()
            return

        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS properties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                property_type VARCHAR(50) NOT NULL,
                location VARCHAR(100) NOT NULL,
                city VARCHAR(100) NOT NULL,
                price DECIMAL(12, 2) NOT NULL,
                bedrooms INT DEFAULT 0,
                bathrooms INT DEFAULT 0,
                area_sqft INT DEFAULT 0,
                description TEXT,
                image_url VARCHAR(255),
                status VARCHAR(20) DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                property_id INT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                visit_date DATE NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_message TEXT,
                bot_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


# Initialize the chatbot, giving it access to the DB connection function
chatbot = RealEstateChatbot(get_db_connection)
init_db()


# =====================================================================
# ROUTES
# =====================================================================

@app.route("/")
def home():
    """Home page - shows a hero section and a few featured properties."""
    try:
        featured = _fetch_all("SELECT * FROM properties WHERE status='Available' ORDER BY created_at DESC LIMIT 6")
    except Exception as exc:  # pragma: no cover - defensive fallback
        featured = []
        flash(f"Database connection error: {exc}", "error")

    return render_template("index.html", featured=featured)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/properties", methods=["GET"])
def properties():
    """Property listing page with search/filter by location and budget."""
    location = request.args.get("location", "").strip()
    max_budget = request.args.get("max_budget", "").strip()
    property_type = request.args.get("property_type", "").strip()

    sql = "SELECT * FROM properties WHERE status = 'Available'"
    params = []

    if location:
        sql += " AND (city LIKE ? OR location LIKE ?)"
        params.extend([f"%{location}%", f"%{location}%"])

    if property_type:
        sql += " AND property_type = ?"
        params.append(property_type)

    if max_budget:
        try:
            sql += " AND price <= ?"
            params.append(float(max_budget))
        except ValueError:
            pass

    sql += " ORDER BY price ASC"

    results = []
    try:
        conn = get_db_connection()
        if _is_sqlite(conn):
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            results = [dict(row) for row in cursor.fetchall()]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql.replace("?", "%s"), tuple(params))
            results = cursor.fetchall()
        conn.close()
    except Exception as exc:  # pragma: no cover - defensive fallback
        flash(f"Database error: {exc}", "error")

    return render_template(
        "properties.html",
        properties=results,
        location=location,
        max_budget=max_budget,
        property_type=property_type,
    )


@app.route("/property/<int:property_id>")
def property_detail(property_id):
    """Detail page for a single property."""
    try:
        prop = _fetch_one("SELECT * FROM properties WHERE id = ?", (property_id,))
    except Exception as exc:  # pragma: no cover - defensive fallback
        prop = None
        flash(f"Database error: {exc}", "error")

    if not prop:
        flash("Property not found.", "error")
        return redirect(url_for("properties"))

    return render_template("property_detail.html", property=prop)


@app.route("/book", methods=["GET", "POST"])
def book_visit():
    """Site visit booking form (GET shows form, POST saves booking)."""
    property_id = request.args.get("property_id", type=int)

    all_properties = []
    try:
        all_properties = _fetch_all("SELECT id, title, city FROM properties WHERE status='Available' ORDER BY title")
    except Exception as exc:  # pragma: no cover - defensive fallback
        flash(f"Database error: {exc}", "error")

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
            _write(
                "INSERT INTO bookings (property_id, name, email, phone, visit_date, message) VALUES (?, ?, ?, ?, ?, ?)",
                (selected_property_id, name, email, phone, visit_date, message),
            )
            flash("Your site visit has been booked successfully! Our team will contact you soon.", "success")
            return redirect(url_for("book_visit"))
        except Exception as exc:  # pragma: no cover - defensive fallback
            flash(f"Could not save booking: {exc}", "error")

    return render_template("book_visit.html", properties=all_properties, selected_id=property_id)


@app.route("/chatbot", methods=["POST"])
def chatbot_endpoint():
    """AJAX endpoint used by the chat widget."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    reply = chatbot.get_response(user_message)

    try:
        _write("INSERT INTO chat_logs (user_message, bot_response) VALUES (?, ?)", (user_message, reply))
    except Exception:
        pass

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
