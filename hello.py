from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


#Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "Super duper secret key"


#Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


#Create a Route Decorator
@app.route('/')
def index():
    first_name = "Hank Hill"
    return render_template('index.html', first_name=first_name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

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


#Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)