"""
Initialize FLASK database.
"""
from api import app, db

with app.app_context():
    db.create_all()

# Ensure there is one blank line at the end to avoid error C0303 (trailing-whitespace)