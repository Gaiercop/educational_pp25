import sqlite3
conn = sqlite3.connect('students_tasks.db')
cursor = conn.cursor()

# Создание таблицы с новым полем
cursor.execute('''
CREATE TABLE IF NOT EXISTS students_tasks (
    userid INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    task_count INTEGER DEFAULT 0,
    right_task_count INTEGER DEFAULT 0,
    PRIMARY KEY (userid, task_type)
)
''')


def update_task_count(db, userid, task_type, is_correct):
    try:
        # Значения для вставки и обновления
        initial_count = 1
        correctness_value = 1 if is_correct else 0

        db.execute('''
            INSERT INTO students_tasks (userid, task_type, task_count, right_task_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(userid, task_type) DO UPDATE SET
                task_count = task_count + 1,
                right_task_count = right_task_count + excluded.right_task_count
        ''', (userid, task_type, initial_count, correctness_value))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def get_task_stats(userid, task_type):
    """Возвращает общее количество решений и правильных ответов"""
    cursor.execute('''
    SELECT task_count, right_task_count 
    FROM students_tasks 
    WHERE userid = ? AND task_type = ?
    ''', (userid, task_type))
    result = cursor.fetchone()
    return result if result else (0, 0)


from collections import defaultdict


def get_tasks_stats(userid):
    conn = sqlite3.connect('students_tasks.db')
    cursor = conn.cursor()

    # Получаем статистику по типам задач
    cursor.execute('''
        SELECT 
            task_type,
            SUM(task_count) as total,
            SUM(right_task_count) as correct
        FROM students_tasks
        WHERE userid = ?
        GROUP BY task_type
    ''', (userid,))

    stats = cursor.fetchall()
    conn.close()

    # Формируем словарь
    tasks_stats = defaultdict(dict)
    for task_type, total, correct in stats:
        tasks_stats[task_type] = {
            "total": total,
            "correct": correct
        }

    return dict(tasks_stats)
def reset_database():
    """Полностью пересоздает таблицу с новыми полями"""
    cursor.execute('DROP TABLE IF EXISTS students_tasks')
    cursor.execute('''
    CREATE TABLE students_tasks (
        userid INTEGER NOT NULL,
        task_type TEXT NOT NULL,
        task_count INTEGER DEFAULT 0,
        right_task_count INTEGER DEFAULT 0,
        PRIMARY KEY (userid, task_type)
    )
    ''')
    conn.commit()
    print("База данных успешно сброшена!")
def recreate_tasks_table():
    # Подключение к базе данных (файл students_tasks.db будет создан, если его нет)
    conn = sqlite3.connect('students_tasks.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS tasks')
    # SQL-запрос для создания таблицы
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        options TEXT,
        answer TEXT NOT NULL,
        tags TEXT,
        difficulty INTEGER,
        type TEXT
    );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("Таблица 'tasks' успешно создана или уже существует.")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        conn.close()
def get_task_byid(userid):
    conn = sqlite3.connect('students_tasks.db')
    cursor = conn.cursor()

    # Получаем статистику по типам задач
    cursor.execute('''
        SELECT 
            id,
            text, options,answer,tags,difficulty, type
        FROM tasks
        WHERE id = ?
    ''', (userid,))

    stats = cursor.fetchall()
    conn.close()
    tasks_stats = defaultdict(dict)
    tasks_field = ['id','text','options','answer','tags','difficulty','type']
    for i in range(len(tasks_field)):
        tasks_stats[tasks_field[i]] = stats[0][i]

    return tasks_stats
def get_all_taskid():
    conn = sqlite3.connect('students_tasks.db')
    cursor = conn.cursor()

    # Получаем статистику по типам задач
    cursor.execute('''
           SELECT id
           FROM tasks
       ''')
    data = cursor.fetchall()
    ab = []
    for i in range(len(data)):
        ab.append(data[i][0])
    conn.close()
    return ab
def add_task_byid(text, options, answer, tags, difficulty, type):
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    conn = sqlite3.connect('students_tasks.db')
    cursor = conn.cursor()

    # SQL-запрос для вставки данных в таблицу tasks
    query = '''
    INSERT INTO tasks (text, options, answer, tags, difficulty, type)
    VALUES (?, ?, ?, ?, ?, ?)
    '''

    # Выполняем запрос с переданными параметрами
    cursor.execute(query, (text, options, answer, tags, difficulty, type))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

if __name__ == "__main__":
    recreate_tasks_table()