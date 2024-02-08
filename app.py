from flask import Flask,request, redirect,render_template, url_for
from flask_login import LoginManager, login_user,logout_user,current_user, login_required,  UserMixin

app=Flask(__name__)

login_manager = LoginManager(app)

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

@app.route("/register", methods=["GET","POST"])
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
            return redirect(url_for('home'))
            
    return render_template('register.html')
@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")
if __name__=="__main__":
    app.run(debug=True)


