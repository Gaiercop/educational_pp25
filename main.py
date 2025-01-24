from flask import Flask, render_template, request
from auth import *

auth = AuthManager()

app = Flask(__name__)

@app.route('/catalogs')
def catalogs():
    catalogs = ['Electronics', 'Books', 'Clothing', 'Home & Garden']
    return render_template('catalogs.html', catalogs=catalogs)

@app.route('/tests')
def tests():
    return render_template('test.html')

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

@app.route('/register', methods=["POST", "GET"])
def register():
    message = 'Заполните поля для регистрации'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        access = request.form['access']
        if (access == 'Ученик'):
            access = 1
        else:
            access = 2
        try:
            auth.addUser(User(username, password, access))
            message = 'Вы успешно зарегистрировались'
        except:
            message = 'Ошибка, попробуйте еще раз'

    return render_template("register.html", message=message)

#322

@app.route('/course/<id>')
def course(id: int):
    return render_template("course.html")
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)