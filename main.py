from flask import Flask, render_template, request, redirect, url_for, abort, g
from auth import AuthManager, User
import os
import time
import json
from datetime import datetime
from get_themebyid import *
from statistics import *
app = Flask(__name__)
auth = AuthManager()
app.auth = auth

# Конфигурация
COURSES_DIR = "./courses"
TESTS_DIR = "./tests"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/group_avatars'


@app.context_processor
def inject_vars():
    return dict(
        auth=auth,
        url_for=url_for,
        request=request
    )


@app.template_filter('datetime_format')
def datetime_format(value):
    if value is None:
        return ""
    return datetime.fromisoformat(value).strftime('%d.%m.%Y %H:%M')


def get_user_groups(username: str):
    groups_file = 'groups/groups.json'
    user_groups = []

    try:
        with open(groups_file, 'r', encoding='utf-8') as f:
            all_groups = json.load(f)

        for group in all_groups:
            if username in group.get('members', []) or username == group.get('creator_id'):
                members = group.get('members', [])

                group_data = {
                    'id': group.get('id'),
                    'name': group.get('name'),
                    'access_level': group.get('access_level', 'private'),
                    'members': group.get('members', []),
                    'created_at': group.get('created_at'),
                    'members_count': len(members),
                }
                user_groups.append(group_data)

    except Exception as e:
        print(f"Error loading groups: {str(e)}")

    return user_groups


def get_current_user(sid: str):
    return auth.get_user_by_session(sid) if sid else None


def handle_authentication(sid: str):
    if not sid or not auth.check_session(sid):
        return redirect(url_for('login') + f'?sid={sid}')
    return None


@app.route('/logout')
def logout():
    sid = request.args.get('sid')
    if sid:
        auth.terminate_session(sid)
    return redirect(url_for('index'))


# ================== Группы ==================

def get_group_by_id(group_id):
    groups_file = 'groups/groups.json'
    if not os.path.exists(groups_file):
        return None

    with open(groups_file, 'r', encoding='utf-8') as f:
        groups = json.load(f)
        return next((g for g in groups if g['id'] == group_id), None)


def update_group(updated_group):
    groups_file = 'groups/groups.json'
    with open(groups_file, 'r+', encoding='utf-8') as f:
        groups = json.load(f)
        index = next(i for i, g in enumerate(groups) if g['id'] == updated_group['id'])
        groups[index] = updated_group
        f.seek(0)
        json.dump(groups, f, ensure_ascii=False, indent=4)
        f.truncate()


@app.route('/group/<group_id>', methods=['GET', 'POST'])
def group_page(group_id):
    sid = request.args.get('sid')
    user = auth.get_user_by_session(sid)

    group = get_group_by_id(group_id)
    if not group:
        abort(404)

    if not user or user.username not in group['members']:
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST' and user.username == group['creator_id']:
        action = request.form.get('action')
        target_user = request.form.get('username')

        if action == 'add':
            if auth.find_user(target_user):
                if target_user not in group['members']:
                    group['members'].append(target_user)
                    update_group(group)
                else:
                    error = "Пользователь уже в группе"
            else:
                error = "Пользователь не найден"

        elif action == 'remove':
            if target_user in group['members'] and target_user != group['creator_id']:
                group['members'].remove(target_user)
                update_group(group)

    return render_template('group_page.html',
                           sid=sid,
                           group=group,
                           user=user,
                           error=error)


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    sid = request.args.get('sid')
    auth_check = handle_authentication(sid)
    if auth_check:
        return auth_check

    user = get_current_user(sid)
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            group_data = {
                "id": str(int(time.time() * 1000)),
                "name": request.form.get('group_name'),
                "description": request.form.get('description'),
                "access_level": request.form.get('access_level', 'public'),
                "creator_id": user.username,
                "members": [user.username],
                "created_at": datetime.now().isoformat()
            }

            if not group_data['name']:
                return render_template('create_group.html',
                                       sid=sid,
                                       error="Название группы обязательно")

            groups_file = 'groups/groups.json'
            os.makedirs(os.path.dirname(groups_file), exist_ok=True)

            groups = []
            if os.path.exists(groups_file):
                with open(groups_file, 'r', encoding='utf-8') as f:
                    groups = json.load(f)

            groups.append(group_data)

            with open(groups_file, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=4)

            return redirect(url_for('profile', sid=sid))

        except Exception as e:
            print(f"Error creating group: {str(e)}")
            return render_template('create_group.html', sid=sid,
                                   error="Ошибка при создании группы")

    return render_template('create_group.html', sid=sid)


# ================== Теория ==================
@app.route('/teory/<nomer>')
def teory(nomer):
    sid = request.args.get('sid')
    try:
        with open(f"teory/{nomer}.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        with open("relocate.json", "r", encoding='utf-8') as f:
            relo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки данных: {str(e)}")
        abort(404)

    return render_template('teory.html', teory=data, relo=relo, sid=sid)


# ================== Форум ==================
@app.route('/forum')
def forum():
    sid = request.args.get('sid')
    theme_list = get_all_theme_ids()
    theme = [get_theme_by_id(i) for i in theme_list]
    return render_template('forum_main.html', popular_themes=theme, sid=sid)


@app.route('/forum/new_post', methods=['GET', 'POST'])
def do_post():
    sid = request.args.get('sid')
    auth_check = handle_authentication(sid)
    if auth_check:
        return auth_check

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        theme_id = create_theme(title, description)
        return redirect(url_for("show_theme", theme_id=theme_id, sid=sid))

    return render_template('create_post.html', sid=sid)


@app.route('/forum/topic/<theme_id>', methods=['GET', 'POST'])
def show_theme(theme_id):
    sid = request.args.get('sid')
    user = get_current_user(sid)

    if request.method == 'POST':
        if not user:
            au = "Гость"
        else:
            au = user.username
        add_new_message(theme_id, au, request.form['content'])

    theme = get_theme_by_id(theme_id)
    posts = get_messages_by_theme_id(theme_id)
    return render_template('theme_page.html',
                           theme=theme,
                           posts=posts,
                           sid=sid,
                           rq=0 if user else 1)


# ================== Курсы и задания ==================
@app.route('/catalogs')
def catalogs():
    sid = request.args.get('sid')
    with open("courses.json", "r", encoding="utf-8") as f:
        arr = json.load(f)
    catalogs = {list(d.keys())[0]: d[list(d.keys())[0]] for d in arr}
    return render_template('catalogs.html', catalogs=catalogs, sid=sid)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('students_tasks.db')
        g.db.row_factory = sqlite3.Row
    return g.db


# Функция для закрытия подключения
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Регистрируем функцию закрытия в приложении
app.teardown_appcontext(close_db)


@app.route('/submit_task', methods=['POST'])
def submit_task():
    sid = request.form.get('sid')
    task_id = request.form.get('task_id')
    selected_answer = request.form.get('answer')
    user = auth.get_user_by_session(sid)
    if (user):
        user = user.username
    else:
        user = "незарегистрированный пользователь"
    # Получаем userid из сессии
    userid = sid
    # Загрузка задач и поиск текущей
    with open("tasks.json", 'r', encoding='utf-8') as f:
        tasks = json.load(f)
        current_task = next((t for t in tasks if t['id'] == int(task_id)), None)

    if not current_task:
        return "Задача не найдена", 404

    # Определяем тип задачи по первому тегу
    task_type = task_id

    # Нормализуем ответы для сравнения
    correct_answer = current_task['answer'].strip().lower()
    user_answer = selected_answer.strip().lower()

    is_correct = user_answer == correct_answer
    # Обновление статистики в БД
    try:
        db = get_db()
        update_task_count(db, user, task_type, is_correct)
    except Exception as e:
        print(f"Ошибка обновления БД: {e}")
        return "Ошибка сервера", 500

    return redirect(url_for('tasks', sid=sid))


@app.route('/tasks')
def tasks():
    sid = request.args.get('sid')
    selected_tags = request.args.getlist('tags')

    with open("tasks.json", 'r', encoding='utf-8') as f:
        tsks = json.load(f)

    filtered_tasks = tsks
    if selected_tags:
        filtered_tasks = [task for task in tsks
                          if any(tag in task['tags'] for tag in selected_tags)]

    all_tags = {tag for task in tsks for tag in task['tags']}
    return render_template('tasks.html',
                           tasks=filtered_tasks,
                           all_tags=all_tags,
                           sid=sid)


# ================== Тесты ==================
@app.route('/tests')
def tests():
    return render_template('test.html', sid=request.args.get('sid'))


@app.route('/course/<int:course_id>/test/<int:test_id>')
def test(course_id, test_id):
    sid = request.args.get('sid')
    test_file = os.path.join(TESTS_DIR, f"{course_id}_{test_id}.json")

    if not os.path.exists(test_file):
        abort(404, description="Test not found")

    with open(test_file, 'r', encoding='utf-8') as file:
        test_data = json.load(file)

    return render_template("test.html",
                           test=test_data,
                           course_id=course_id,
                           test_id=test_id,
                           sid=sid)


# ================== Аутентификация ==================
@app.route('/login', methods=["POST", "GET"])
def login():
    sid = request.args.get('sid')

    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            new_sid = auth.login(username, password)
            return redirect(url_for('index') + f'?sid={new_sid}')
        except ValueError as e:
            return render_template("login.html",
                                   message=str(e),
                                   sid=sid)

    return render_template("login.html",
                           message='Введите логин и пароль',
                           sid=sid)


@app.route('/register', methods=["POST", "GET"])
def register():
    sid = request.args.get('sid')

    if request.method == 'POST':
        try:
            user = User(
                username=request.form['username'],
                pwd=request.form['password'],
                access=1 if request.form['access'] == 'Ученик' else 2
            )
            auth.add_user(user)
            return redirect(url_for('login'))
        except ValueError as e:
            return render_template("register.html",
                                   message=str(e),
                                   sid=sid)

    return render_template("register.html",
                           message='Заполните поля для регистрации',
                           sid=sid)


# ================== Профиль и курс ==================
@app.route('/profile')
def profile():
    sid = request.args.get('sid')
    user = auth.get_user_by_session(sid)

    if not user:
        return redirect(url_for('login'))

    return render_template("profile.html",
                           sid=sid,
                           username=user.username,
                           access="Учитель" if int(user.access) == 2 else "Ученик",
                           groups=get_user_groups(user.username))


@app.route('/course/<int:course_id>')
def course(course_id):
    sid = request.args.get('sid')
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")

    if not os.path.exists(course_file):
        abort(404, description="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        course_data = json.load(file)

    try:
        with open("relocate.json", "r", encoding='utf-8') as f:
            relo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        relo = {}

    return render_template("course.html",
                           sid=sid,
                           course=course_data,
                           course_id=course_id,
                           relo=relo)


# ================== Главная страница ==================
@app.route('/')
def index():
    return render_template('index.html', sid=request.args.get('sid'))


if __name__ == '__main__':
    app.run(debug=True)