"""Render/Gunicorn entrypoint.

This lets both `gunicorn app:app` and
`gunicorn real_estate_chatbot.app:app` start the same Flask application.
"""

from real_estate_chatbot.app import app

