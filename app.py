from flask import Flask,request, redirect,render_template, url_for
from flask_login import LoginManager, login_user,logout_user,current_user, login_required,  UserMixin
from flask_sqlalchemy import SQLAlchemy
import os

app=Flask(__name__)

login_manager = LoginManager(app)
db=SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
# Example User model
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Example user loader function
@login_manager.user_loader
def load_user(user_id):
    # Example: Load user from a database using the provided user_id
    return User(user_id)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        if not (fullname and username and email and password):
            error_message = 'All fields are required.'
            return render_template('register.html', error_message=error_message)
        else:
            # Assuming registration logic here (e.g., adding user to database)
            # Redirect to home page after successful registration
            # For now, just print the form data for testing
            print(f"Username: {username}, Full Name: {fullname}, Email: {email}, Password: {password}")
            return "User registered successfully"

    # Render the register.html template for GET requests
    return render_template('register.html')
    # return render_template("register.html")
    # username = request.form['username']
    
   

#handlig databases


# @app.route("/login", methods=["GET", "POST"])
# def login():

if __name__=="__main__":
    app.run(debug=True)

