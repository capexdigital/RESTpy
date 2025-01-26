"""
This module defines the API endpoints and database models for a Flask application.
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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
        """
        Retrieve all users.

        Returns:
            list: A list of all users.
        """
        users = UserModel.query.all()
        return users

# Define User resource
class User(Resource):
    """
    Resource for managing a single user.
    """
    @marshal_with(user_fields)
    def get(self, user_id):
        """
        Retrieve a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            UserModel: The user object.

        Raises:
            404: If the user is not found.
        """
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        return user

    @marshal_with(user_fields)
    def patch(self, user_id):
        """
        Update a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            UserModel: The updated user object.

        Raises:
            404: If the user is not found.
        """
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
        """
        Delete a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of all remaining users.

        Raises:
            404: If the user is not found.
        """
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        """
        Create a new user.

        Returns:
            tuple: A tuple containing the list of all users and the HTTP status code 201.
        """
        args = user_args.parse_args()
        user = UserModel(name=args["name"], email=args['email'])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

# Add resources to the API
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>')

# Define home route
@app.route('/')
def home():
    """
    Render the home page.

    Returns:
        str: The rendered HTML template.
    """
    return render_template('index.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
