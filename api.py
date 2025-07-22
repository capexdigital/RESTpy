"""
This module defines the API endpoints and database models for a Flask application.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
api = Api(app)

# pylint: disable=too-few-public-methods
class UserModel(db.Model):
    """
    Represents user in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

# Define request parser for user input
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

# Define response fields for marshaling
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

# Define Users resource
class Users(Resource):
    """
    Resource for managing multiple users.
    """
    @marshal_with(user_fields)
    def get(self):
        users = UserModel.query.all()
        return users

# Define User resource
class User(Resource):
    """
    Resource for managing a single user.
    """
    @marshal_with(user_fields)
    def get(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        return user

    @marshal_with(user_fields)
    def patch(self, user_id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user

    @marshal_with(user_fields)
    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args["name"], email=args['email'], password=generate_password_hash("default"))
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

# Add resources to the API
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>')

# Auth routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        user = UserModel.query.filter_by(name=name).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        user = UserModel(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = UserModel.query.get(session['user_id'])
    return f"Welcome, {user.name}!"

# Run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)