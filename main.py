from flask import Flask, render_template, request, redirect, url_for
from auth import *
from get_themebyid import *
auth = AuthManager()

app = Flask(__name__)
@app.route('/forum')
def forum():
    theme_list = get_all_theme_ids()
    theme = []
    for i in theme_list:
        theme.append(get_theme_by_id(i))
    return render_template('forum_main.html', popular_themes = theme)

@app.route('/forum/new_post', methods=['GET', 'POST'])
def do_post():
     if request.method == 'POST':
         title = request.form['title']
         description = request.form['description']
         theme_id = create_theme(title, description)
         return redirect(url_for("show_theme", theme_id = theme_id))
     return render_template('create_post.html') # Render create theme form

@app.route('/forum/topic/<theme_id>', methods = ['GET', 'POST'])
def show_theme(theme_id):
    if request.method == 'POST':
        au = request.form['author']
        cont = request.form['content']
        add_new_message(theme_id, au, cont)
    theme = get_theme_by_id(theme_id)
    posts = get_messages_by_theme_id(theme_id)
    return render_template('theme_page.html', theme=theme, posts = posts)

@app.route('/catalogs')
def catalogs():
    jsfile = open("courses.json", "r", encoding="utf-8")
    arr = json.load(jsfile)
    catalogs = dict()
    for d in arr:
        key = list(d.keys())[0]
        catalogs[key] = d[key]
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
    k = int(id)+int(1)
    st = "cours/course"+str(k)+".html"
    print(st)
    return render_template(st)
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)