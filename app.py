from flask import Flask, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, EmailField, PasswordField,
    BooleanField, ValidationError)
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from datetime import date
# import MySQLdb


#-----------#
#--CONFIGS--#

#Create a Flask Instance
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#Add Database
#Old SQLite db
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
#New MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:password123@localhost/our_users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#Secret Key
app.config['SECRET_KEY'] = "Super duper secret key"

#Initialize the Database
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
migrate = Migrate(app, db)

#------------------#
#--End of CONFIGS--#


#-------------#
#--DB MODELS--#

#Create Database Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    #Password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Create a String
    def __repr__(self):
        return '<Name %r>' % self.name
#--------------------------#    
#--End of DATABASE MODELS--#    


#----------------#
#--FORM CLASSES--#

#Create a Form Class for Users
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField(
        "Password", 
        validators=[DataRequired(), 
        EqualTo('password_hash2', 
        message='Passwords must match!')]
        )
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a Form Class
class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#-----------------------#
#--End of FORM CLASSES--#


#--------------------#
#--ROUTE DECORATORS--#

#Home page
@app.route('/')
def index():
    first_name = "Hank Hill"
    return render_template('index.html', first_name=first_name)


#Delete user
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User successfully deleted ")

        our_users = Users.query.order_by(Users.date_added)
        return render_template(
            'add_users.html', 
            form=form,
            name=name, 
            our_users=our_users
            )
    except:
        flash("There was a problem deleting the user...")
        return render_template(
            'add_users.html', 
            form=form,
            name=name, 
            our_users=our_users
            )

#Display name entered into form
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form =NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash(f"Hello, { name }! Form was submitted successfully.")
    return render_template('name.html', name=name, form=form)

#Say hello to user(test page)
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

#Add new user
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data,'sha256')
            user = Users(
                name=form.name.data, 
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw
                )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash("User added successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template(
        'add_users.html', 
        form=form,
        name=name, 
        our_users=our_users
        )

#Update User
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_id(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try: 
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem. Please try again.")
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


#Create test password page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form =PasswordForm()
    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''

        #Lookup User by email
        pw_to_check = Users.query.filter_by(email=email).first()

        #Check password hash
        passed = check_password_hash(pw_to_check.password_hash, password)

        #flash(f"Hello, { email }! Form was submitted successfully.")
    return render_template(
        'test_pw.html', 
        email=email, 
        password=password, 
        pw_to_check=pw_to_check,
        passed=passed, 
        form=form)  


#JSON API
@app.route('/date')
def get_current_date():
    # Get the current date and time
    now = datetime.now()

    # Format the date and time
    formatted_date = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%H:%M:%S")

    return {"Date": formatted_date, "Time": formatted_time}
   
#---------------------------#
#--End of ROUTE DECORATORS--#


#---------------#
#--ERROR PAGES--#

#Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Server Error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

#I'm a Little Teapot
@app.errorhandler(418)
def teapot(e):
    return render_template("teapot.html"), 418

#--End of ERROR PAGES--#
#----------------------#


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)