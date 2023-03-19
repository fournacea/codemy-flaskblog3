from flask import Flask, render_template

#Create a Flask Instance
app = Flask(__name__)

#Create a Route Decorator
@app.route('/')
def index():
    first_name = "Hank Hill"
    return render_template('index.html', first_name=first_name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


#Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)