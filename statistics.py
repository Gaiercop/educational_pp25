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