from flask import Flask,flash, request, redirect, render_template, url_for, render_template_string, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import bcrypt
import os

app = Flask(__name__)
app.config['SECRET_KEY']='efaf54030445f83f13a6732ee4b88c38'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DEV_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Xas#123ad@localhost/my_storage'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class LikeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('text_model.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.relationship('TextModel', backref='likes', lazy=True)
    user = db.relationship('UserModel', backref='likes', lazy=True)
class CommentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('text_model.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    text = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.relationship('TextModel', backref='comments', lazy=True)
    user = db.relationship('UserModel', backref='comments', lazy=True)
class RepostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('text_model.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.relationship('TextModel', backref='reposts', lazy=True)
    user = db.relationship('UserModel', backref='reposts', lazy=True)
class TextModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('UserModel', backref='texts', lazy=True)
    like_count = db.Column(db.Integer, default=0)  # Add like_count attribute

class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    

    def __init__(self, username, fullname, email, password):
        self.username = username
        self.fullname = fullname
        self.email = email
        self.password = password

# Example User model
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Example user loader function
@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(user_id)

        
@app.route("/post", methods=["POST"])
def post_text():
    if request.method == "POST":
        text_content = request.form.get("text")
        user_id = request.form.get("user_id")

        # Create a new TextModel object and add it to the database session
        new_text = TextModel(text=text_content, user_id=user_id, created_at=datetime.utcnow())
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for("dashboard"))

@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    is_liked = request.json.get('isLiked')
    post = TextModel.query.get_or_404(post_id)

    if is_liked:
        post.like_count -= 1
    else:
        post.like_count += 1

    db.session.commit()

    return jsonify({
        'like_count': post.like_count,
        'is_liked': not is_liked
    })
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))

        if not (fullname and username and email and password):
            error_message = 'All fields are required.'
            return render_template('register.html', error_message=error_message)
        else:
            # Check if the email or username already exists in the database
            existing_user_email = UserModel.query.filter_by(email=email).first()
            existing_user_username = UserModel.query.filter_by(username=username).first()

            if existing_user_email:
                error_message = 'Email address is already in use.'
                return render_template('register.html', error_message=error_message)
            elif existing_user_username:
                error_message = 'Username is already taken.'
                return render_template('register.html', error_message=error_message)
            else:
                new_user = UserModel(username=username, fullname=fullname, email=email, password=password_hash)
                db.session.add(new_user)
                try:
                    db.session.commit()
                    return redirect(url_for("home"))
                except IntegrityError as e:
                    db.session.rollback()
                    error_message = 'An error occurred while registering the user: ' + str(e)
                    return render_template('register.html', error_message=error_message)

    return render_template("register.html")

    

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = UserModel.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Password is correct, log the user in
            login_user(user)
            # Redirect to a protected route after successful login
            login_user(user)
            return redirect(url_for("dashboard"))
            
        else:
            # Incorrect email or password, handle authentication failure
            error_message = "Invalid email or password. Please try again."
            return render_template("home.html", error_message=error_message)
    return render_template("home.html")

def get_initials(fullname):
    names = fullname.split()
    initials = "".join(name[0].upper() for name in names)
    return initials

app.jinja_env.filters['initials'] = get_initials
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    all_posts = TextModel.query.all()
    return render_template("dashboard.html", posts=all_posts)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)