"""
Initialize FLASK database.
"""
from api import app, db

with app.app_context():
    db.create_all()

# The end