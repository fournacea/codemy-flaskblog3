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


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)