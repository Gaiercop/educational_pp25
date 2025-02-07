from flask import Flask, render_template, request, redirect, url_for, abort, g
from auth import AuthManager, User
import os
import time
import json
from datetime import datetime
from get_themebyid import *
from statistics import *
from hashlib import *
import uuid

app = Flask(__name__)
auth = AuthManager()
app.auth = auth

# Конфигурация
COURSES_DIR = "./courses"
TESTS_DIR = "./tests"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/group_avatars'
VARIANTS_DIR = "./variants"


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
                    'token': group.get('token')
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

# Создание варианта теста
@app.route('/create_variant', methods=['GET', 'POST'])
def create_variant():
    sid = request.args.get('sid')
    auth_check = handle_authentication(sid)
    if auth_check:
        return auth_check
    tasks_id = get_all_taskid()
    all_filters = set()
    tasks_data = [[] for i in range(len(tasks_id))]
    for i in range(len(tasks_id)):
        tasks_data[i] = get_task_byid(tasks_id[i])
        tasks_data[i]['options'] = tasks_data[i]['options'].split(';')

        tasks_data[i]['tags'] = tasks_data[i]['tags'].split(';')
        for tag in tasks_data[i]['tags']:
            all_filters.add(tag)
    selected_tags = []
    all_filters = ["орфоэпия",
                   "паронимы", "лексические_нормы", "морфологические_нормы", "синтаксические_нормы",
                   "правописание_корней", "правописание_приставок", "правописание_суффиксов", "правописание_глаголов",
                   "правописание_причастий", "правописание_не", "слитное_раздельное_написание", "н_нн",
                   "знаки_препинания_простое_предложение", "знаки_препинания_обособленные_конструкции",
                   "знаки_препинания_вводные_слова", "знаки_препинания_сложное_предложение", "средства_выразительности",
                   "сочинение_егэ", "аргументы_к_сочинению"]
    res = []
    for task in tasks_data:
        cur = task['tags']
        fl = 0
        for tag in selected_tags:
            if (tag not in cur):
                fl = 1
        if (fl == 0):
            res.append(task)
    tasks_data = res[::]
    user = get_current_user(sid)
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_ids = list(map(int, request.form.getlist('selected_tasks')))
        check_system = request.form.get('check')
        check_id = int()
        
        if check_system == "Полная": check_id = 0
        elif check_system == "Частичная": check_id = 1
        elif check_system == "Только баллы": check_id = 2
        else: check_id = 3
        
        with open("tasks.json", 'r', encoding='utf-8') as f:
            all_tasks = json.load(f)

        selected_tasks = []
        for task_id in selected_ids:
            task_data = get_task_byid(task_id)
            task_data['options'] = task_data['options'].split(';')
            task_data['tags'] = task_data['tags'].split(';')
            selected_tasks.append(task_data)
        print(selected_tasks)
        variant_id = str(uuid.uuid4())[:8]
        variant_data = {
            'id': variant_id,
            'created_at': datetime.now().isoformat(),
            'tasks': selected_tasks,
            'created_by': user.username,
            'check': check_id,
        }

        os.makedirs(VARIANTS_DIR, exist_ok=True)
        with open(os.path.join(VARIANTS_DIR, f"{variant_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(variant_data, f, ensure_ascii=False, indent=4)
        
        return redirect(url_for('profile', variant_id=variant_id, sid=sid))
    
    with open("tasks.json", 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    return render_template('create_variant.html', tasks=tasks_data, sid = sid)

# Решение варианта
@app.route('/solve_variant/<variant_id>', methods=['GET', 'POST'])
def solve_variant(variant_id):
    sid = request.args.get('sid')
    variant_file = os.path.join(VARIANTS_DIR, f"{variant_id}.json")
    if not os.path.exists(variant_file):
        abort(404)

    auth_check = handle_authentication(sid)
    if auth_check:
        return auth_check

    user = get_current_user(sid)
    if not user:
        return redirect(url_for('login'))

    with open(variant_file, 'r', encoding='utf-8') as f:
        variant_data = json.load(f)

    if request.method == 'POST':
        correct = 0
        results = []

        for task in variant_data['tasks']:
            user_answer = request.form.get(f'task_{task["id"]}')
            is_correct = user_answer == task['answer']
            if is_correct:
                correct += 1
            results.append({
                'task_id': task['id'],
                'correct': is_correct,
                'user_answer': user_answer,
                'correct_answer': task['answer']
            })

        score = f"{correct}/{len(variant_data['tasks'])}"
        return render_template('variant_results.html', score=score, results=results, check_id = variant_data['check'], sid=sid)

    return render_template('solve_variant.html', variant=variant_data, sid=sid)



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

@app.route('/join_group', methods=['GET', 'POST'])
def join_group_by_token():
    sid = request.args.get('sid')
    auth_check = handle_authentication(sid)
    if auth_check:
        return auth_check

    user = get_current_user(sid)
    if not user:
        return redirect(url_for('login'))

    message = 'Введите токен, данный учителем для присоединения к группе'

    groups_file = 'groups/groups.json'
    if (request.method == "POST"):
        token = request.form.get("token")
        groups = []
        if os.path.exists(groups_file):
            with open(groups_file, 'r', encoding='utf-8') as f:
                groups = json.load(f)

        for group in groups:
            if (group['token'] == token):

                if user not in group['members']:
                    group['members'].append(user.username)
                    update_group(get_group_by_id(group['id']))
                    message = "Вы успешно добавлены в группу"
                else:
                    message = "Вы уже есть в этой группе"

        with open(groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=4)
        if (len(message) == 0):
            message = 'Группы с таким токеном нет'

    return render_template("join_group_by_token.html", message=message, sid=sid)


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
                "created_at": datetime.now().isoformat(),
                "token": sha256((str(datetime.now().isoformat()) + str(int(time.time() * 1000)) + str(user.username)).encode()).hexdigest()
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
    task_type = request.form.get('task_type')
    selected_answer = request.form.get('answer')
    print(selected_answer)
    user = auth.get_user_by_session(sid)
    if (user):
        user = user.username
    else:
        user = "незарегистрированный пользователь"
    task = get_task_byid(task_id)
    correct_answer = task['answer'].strip().lower()
    user_answer = selected_answer.strip().lower()
    print("ok")
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
    tasks_id = get_all_taskid()
    if not auth.check_session(sid) if sid else False:
        return redirect(url_for('login'))
    all_filters = set()
    tasks_data = [[] for i in range (len(tasks_id))]
    for i in range(len(tasks_id)):
        tasks_data[i] = get_task_byid(tasks_id[i])
        tasks_data[i]['options'] = tasks_data[i]['options'].split(';')

        tasks_data[i]['tags'] = tasks_data[i]['tags'].split(';')
        for tag in tasks_data[i]['tags']:
           all_filters.add(tag)
    selected_tags = request.args.getlist('tags')
    all_filters = ["орфоэпия",
                   "паронимы", "лексические_нормы", "морфологические_нормы", "синтаксические_нормы",
                   "правописание_корней", "правописание_приставок", "правописание_суффиксов", "правописание_глаголов",
                   "правописание_причастий", "правописание_не", "слитное_раздельное_написание", "н_нн",
                   "знаки_препинания_простое_предложение", "знаки_препинания_обособленные_конструкции",
                   "знаки_препинания_вводные_слова", "знаки_препинания_сложное_предложение", "средства_выразительности",
                   "сочинение_егэ", "аргументы_к_сочинению"]
    print(selected_tags)
    res = []
    for task in tasks_data:
        cur = task['tags']
        fl = 0
        for tag in selected_tags:
            if(tag not in cur):
                fl = 1
        if(fl == 0):
            res.append(task)
    tasks_data = res[::]
    return render_template('tasks.html',
                         all_tags=all_filters,
                         sid=sid, tasks_data = tasks_data)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        text = request.form['text']
        options = request.form['options']
        answer = request.form['answer']
        tags = request.form.getlist('tags')
        t = ""
        for i in range(len(tags)-1):
            t += tags[i]+';'
        tags = t
        difficulty = request.form['difficulty']
        type = request.form['type']
        add_task_byid(text,options,answer, tags,difficulty,type)
        return redirect(url_for('tasks'))  # Замените 'tasks_page' на имя вашей функции представления для страницы с заданиями
    else:
        sid = request.args.get('sid')
        tasks_id = get_all_taskid()
        if not auth.check_session(sid) if sid else False:
            return redirect(url_for('login'))

        all_filters= [  "орфоэпия",
    "паронимы", "лексические_нормы","морфологические_нормы", "синтаксические_нормы", "правописание_корней", "правописание_приставок",  "правописание_суффиксов", "правописание_глаголов", "правописание_причастий", "правописание_не", "слитное_раздельное_написание",   "н_нн","знаки_препинания_простое_предложение",  "знаки_препинания_обособленные_конструкции",  "знаки_препинания_вводные_слова",  "знаки_препинания_сложное_предложение", "средства_выразительности",  "сочинение_егэ",  "аргументы_к_сочинению"]
    return render_template('add_task.html', all_tags=all_filters)

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
                access=1 if request.form['access'] == 'Ученик' else 2,
                birthday=str(datetime.strptime(request.form['birthday'], "%Y-%m-%d").date()),
                email=request.form['email']
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
    if not auth.check_session(sid) if sid else False:
        return redirect(url_for('login'))

    user = auth.get_user_by_session(sid)

    if not user:
        return redirect(url_for('login'))
    
    userid = user.username
    tasks_stats = get_tasks_stats(userid)
    total_tasks = sum(stats['total'] for stats in tasks_stats.values())
    variants = []
    
    for file in os.listdir(VARIANTS_DIR):
        filename = os.fsdecode(file)
        with open(VARIANTS_DIR + '/' + filename, 'r', encoding = 'utf-8') as f:
            variant = json.load(f)
            if variant['created_by'] == userid:
                variants.append(variant)
    
    user_groups = get_user_groups(user.username)

    all_members = set()
    for group in user_groups:
        all_members.update(group.get('members', []))

    all_users = auth.users

    students_count = sum(
        1 for username in all_members
        if any(u.username == username and int(u.access) == 1 for u in all_users)
    )

    return render_template("profile.html",
                           sid=sid,
                           username=user.username,
                           access="Учитель" if int(user.access) == 2 else "Ученик",
                           groups=user_groups,
                           students_count=students_count, tasks_stats=tasks_stats,
                           birthday=user.birthday, email=user.email,
                                           variants=variants,
        total_tasks=total_tasks)


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
