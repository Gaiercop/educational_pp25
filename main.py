from flask import Flask, render_template, request, redirect, url_for, abort
from auth import AuthManager, User
import os
import time
import json
from datetime import datetime
from get_themebyid import *

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

            return redirect(url_for('group_page', group_id=group_data['id'], sid=sid))

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
    user = get_current_user(sid)
    
    if not user:
        return redirect(url_for('login'))
    
    access_map = {1: "Ученик", 2: "Учитель"}
    return render_template("profile.html", 
                         sid=sid, 
                         username=user.username, 
                         access=access_map.get(user.access, "Гость"))

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
