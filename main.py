from flask import Flask, render_template, request
from auth import *

auth = AuthManager()


app = Flask(__name__)

@app.route('/catalogs')
def catalogs():
    catalogs = ['Electronics', 'Books', 'Clothing', 'Home & Garden']
    return render_template('catalogs.html', catalogs=catalogs)



@app.route('/login', methods=["POST", "GET"])
def login():
    message = 'Введите логин и пароль'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            sid = auth.login(username, password)
            message = "Вы успешно вошли в систему"
        except NameError:
            message = "Неверные логин или пароль"

    return render_template("login.html", message=message)


@app.route('/registration', methods=["POST", "GET"])
def login():
    return render_template("registration.html")


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)