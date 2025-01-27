from types import NoneType

from flask import Flask, render_template, request, redirect, url_for, abort
from auth import *
from get_themebyid import *
import os

auth = AuthManager()

app = Flask(__name__)
COURSES_DIR = "./courses"
TESTS_DIR = "./tests"


@app.route('/forum')
def forum():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1

    theme_list = get_all_theme_ids()
    theme = []
    for i in theme_list:
        theme.append(get_theme_by_id(i))
    return render_template('forum_main.html', popular_themes=theme, sid=str(sid))


@app.route('/forum/new_post', methods=['GET', 'POST'])
def do_post():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        theme_id = create_theme(title, description)
        return redirect(url_for("show_theme", theme_id=theme_id))
    return render_template('create_post.html', sid=str(sid))  # Render create theme form


@app.route('/forum/topic/<theme_id>', methods=['GET', 'POST'])
def show_theme(theme_id):
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    if request.method == 'POST':
        au = request.form['author']
        cont = request.form['content']
        add_new_message(theme_id, au, cont)
    theme = get_theme_by_id(theme_id)
    posts = get_messages_by_theme_id(theme_id)
    return render_template('theme_page.html', theme=theme, posts=posts, sid=str(sid))


@app.route('/catalogs')
def catalogs():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    jsfile = open("courses.json", "r", encoding="utf-8")
    arr = json.load(jsfile)
    catalogs = dict()
    for d in arr:
        key = list(d.keys())[0]
        catalogs[key] = d[key]
    return render_template('catalogs.html', catalogs=catalogs, sid=str(sid))


@app.route('/tasks')  # Определяем endpoint /tasks
def tasks():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    # Ваш код для обработки запроса /tasks
    tasks_list = ['Task 1', 'Task 2', 'Task 3']  # Пример списка
    return render_template('tasks.html', tasks=tasks_list, sid=str(sid))


@app.route('/tests')
def tests():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    return render_template('test.html', sid=str(sid))


@app.route('/course/<int:course_id>/test/<int:test_id>')
def test(course_id, test_id):
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    test_file = os.path.join(TESTS_DIR, f"{course_id}_{test_id}.json")

    if not os.path.exists(test_file):
        abort(404, description="Test not found")

    with open(test_file, 'r', encoding='utf-8') as file:
        test_data = json.load(file)

    return render_template("test.html", test=test_data, course_id=course_id, test_id=test_id, sid=str(sid))


@app.route('/course/<int:course_id>/test/<int:test_id>/result')
def test_result(course_id, test_id):
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    test_name = "Тест 1"
    correct_answers = 3
    total_questions = 5
    return render_template(
        'test_result.html',
        test={"name": test_name},
        correct_answers=correct_answers,
        total_questions=total_questions,
        course_id=course_id,
        test_id=test_id
    )


@app.route('/login', methods=["POST", "GET"])
def login():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            auth.terminateSID(int(sid))
            sid = -1
        else:
            sid = -1
    message = 'Введите логин и пароль'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            sid = auth.login(username, password)
            message = "Вы успешно вошли в систему"
            return redirect(url_for('index') + '?sid=' + str(sid))
        except NameError:
            message = "Неверные логин или пароль"

    return render_template("login.html", message=message, sid=str(sid))


@app.route('/register', methods=["POST", "GET"])
def register():
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            auth.terminateSID(int(sid))
            sid = -1
        else:
            sid = -1
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

    return render_template("register.html", message=message, sid="-1")


@app.route('/profile', methods=["GET"])
def profile():
    return render_template("profile.html", sid="-1")


# 322

@app.route('/course/<int:course_id>')
def course(course_id):
    sid = request.args.get('sid')
    if (type(sid) == NoneType):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")

    if not os.path.exists(course_file):
        abort(404, description="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        course_data = json.load(file)

    return render_template("course.html", course=course_data, course_id=course_id, sid=str(sid))


@app.route('/')
def index():
    sid = request.args.get('sid')
    if (sid == None):
        sid = -1
    else:
        if (auth.checkSID(int(sid))):
            sid = int(sid)
        else:
            sid = -1
    return render_template('index.html', sid=str(sid))


if __name__ == '__main__':
    app.run(debug=True)