from flask import Flask, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate

from datetime import datetime
# import MySQLdb



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
#--End of CONFIGS--#


#--DB MODELS--#
#Create Database Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    #Create a String
    def __repr__(self):
        return '<Name %r>' % self.name
#--End of DATABASE MODELS--#    


#--FORM CLASSES--#
#Create a Form Class for Users
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")

#Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
#--End of FORM CLASSES--#


#--ROUTE DECORATORS--#
@app.route('/')
def index():
    first_name = "Hank Hill"
    return render_template('index.html', first_name=first_name)

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

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form =NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash(f"Hello, { name }! Form was submitted successfully.")
    return render_template("name.html", name=name, form=form)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(
                name=form.name.data, 
                email=form.email.data,
                favorite_color = form.favorite_color.data
                )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash("User added successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template(
        'add_users.html', 
        form=form,
        name=name, 
        our_users=our_users
        )

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


#--End of ROUTE DECORATORS--#


#--ERROR PAGES--#
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500
#--End of ERROR PAGES--#


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)