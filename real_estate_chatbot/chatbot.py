"""
chatbot.py
-----------
A simple rule-based "AI" chatbot for the Real Estate website.

It does NOT require any external AI API or internet access, which
makes it perfect for a college mini project - it runs fully offline.
"""

import re
import sqlite3


class RealEstateChatbot:
    def __init__(self, db_connection_getter):
        """
        db_connection_getter: a function that returns a new database
        connection when called. Passed in from app.py so this class
        does not need to know connection details directly.
        """
        self.get_db_connection = db_connection_getter

        self.known_cities = [
            "bangalore",
            "bengaluru",
            "mumbai",
            "pune",
            "chennai",
            "delhi",
        ]

        self.greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
        self.thanks = ["thanks", "thank you", "thankyou", "thanx"]
        self.bye = ["bye", "goodbye", "see you", "exit"]

    def _query(self, sql, params=None):
        conn = self.get_db_connection()
        try:
            if isinstance(conn, sqlite3.Connection):
                cursor = conn.cursor()
                cursor.execute(sql, params or ())
                return [dict(row) for row in cursor.fetchall()]

            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql.replace("?", "%s"), params or ())
            return cursor.fetchall()
        finally:
            conn.close()

    def _extract_budget(self, text):
        text = text.lower()

        crore_match = re.search(r"(\d+(\.\d+)?)\s*crore", text)
        if crore_match:
            return float(crore_match.group(1)) * 1_00_00_000

        lakh_match = re.search(r"(\d+(\.\d+)?)\s*lakh", text)
        if lakh_match:
            return float(lakh_match.group(1)) * 1_00_000

        plain_match = re.search(r"(\d{5,})", text.replace(",", ""))
        if plain_match:
            return float(plain_match.group(1))

        return None

    def _extract_city(self, text):
        text = text.lower()
        for city in self.known_cities:
            if city in text:
                return "Bangalore" if city == "bengaluru" else city.capitalize()
        return None

    def _extract_property_type(self, text):
        text = text.lower()
        mapping = {
            "villa": "Villa",
            "apartment": "Apartment",
            "flat": "Apartment",
            "plot": "Plot",
            "land": "Plot",
            "independent house": "Independent House",
            "house": "Independent House",
        }
        for keyword, property_type in mapping.items():
            if keyword in text:
                return property_type
        return None

    def _format_properties(self, properties, limit=5):
        if not properties:
            return "I couldn't find any properties matching that. Try a different location, budget, or property type."

        lines = []
        for prop in properties[:limit]:
            price_in_lakh = float(prop["price"]) / 100000
            lines.append(
                f"{prop['title']} - {prop['location']}, {prop['city']} | "
                f"Rs. {price_in_lakh:.1f} Lakh | {prop['bedrooms']}BHK | {prop['area_sqft']} sqft "
                f"(ID: {prop['id']})"
            )

        reply = "Here are some properties I found:\n" + "\n".join(lines)
        if len(properties) > limit:
            reply += f"\n...and {len(properties) - limit} more. Visit the Properties page to see all results!"
        return reply

    def get_response(self, message):
        if not message or not message.strip():
            return "Please type a question about properties, locations, or budget so I can help!"

        text = message.lower().strip()

        if any(word in text for word in self.greetings):
            return (
                "Hello! I'm your AI real estate assistant. You can ask me things like "
                "'Show me 3BHK apartments in Pune under 80 lakh' or "
                "'What villas are available in Chennai?'"
            )

        if any(word in text for word in self.thanks):
            return "You're welcome! Let me know if you'd like help finding more properties."

        if any(word in text for word in self.bye):
            return "Goodbye! Feel free to come back anytime you need help finding your dream home."

        if "help" in text or "what can you do" in text:
            return (
                "I can help you:\n"
                "1. Search properties by location (e.g. 'properties in Mumbai')\n"
                "2. Search by budget (e.g. 'under 50 lakh', 'below 1 crore')\n"
                "3. Search by type (villa, apartment, plot, independent house)\n"
                "4. Answer general questions about buying property\n"
                "5. Help you book a site visit - just ask 'how to book a visit'"
            )

        if "book" in text and "visit" in text:
            return (
                "To book a site visit, go to the 'Book a Visit' page from the menu, "
                "select the property, and fill in your name, phone number, and preferred date. "
                "Our team will confirm your visit shortly!"
            )

        if "emi" in text or "loan" in text:
            return (
                "Most banks offer home loans covering 75-90% of the property value. "
                "EMI depends on loan amount, interest rate, and tenure. "
                "We recommend consulting your bank for an exact EMI calculation."
            )

        if "document" in text or "documents required" in text:
            return (
                "Common documents needed to buy property in India include: ID proof, address proof, "
                "PAN card, sale deed, encumbrance certificate, and property tax receipts. "
                "A legal advisor can help verify these documents before purchase."
            )

        budget = self._extract_budget(text)
        city = self._extract_city(text)
        property_type = self._extract_property_type(text)

        wants_search = any(
            keyword in text
            for keyword in [
                "property",
                "properties",
                "flat",
                "apartment",
                "villa",
                "plot",
                "house",
                "show me",
                "recommend",
                "find",
                "looking for",
                "search",
            ]
        ) or budget or city or property_type

        if wants_search:
            sql = "SELECT * FROM properties WHERE status = 'Available'"
            params = []

            if city:
                sql += " AND city LIKE ?"
                params.append(f"%{city}%")
            if property_type:
                sql += " AND property_type = ?"
                params.append(property_type)
            if budget:
                sql += " AND price <= ?"
                params.append(budget)

            sql += " ORDER BY price ASC"

            try:
                results = self._query(sql, tuple(params))
            except Exception as exc:
                return f"Sorry, I hit a database error while searching: {exc}"

            intro = ""
            if city:
                intro += f"in {city} "
            if property_type:
                intro += f"({property_type}) "
            if budget:
                intro += f"under Rs. {budget / 100000:.1f} Lakh "

            prefix = f"Searching properties {intro}...\n" if intro else ""
            return prefix + self._format_properties(results)

        return (
            "I'm not sure I understood that. You can ask me about property locations, "
            "budgets, property types (villa/apartment/plot), or say 'help' to see what I can do."
        )

