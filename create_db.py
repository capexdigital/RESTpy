"""
Initialize FLASK database.
"""
from api import app, db

with app.app_context():
    db.create_all()

# Add a final newline to the file