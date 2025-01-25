import sqlite3

def create_themes():
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS themes")
    create_post()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created and table 'themes' is ready.")

import sqlite3

def create_post():
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    # Drop the table if it exists
    cursor.execute("DROP TABLE IF EXISTS post")

    # Create the table (always)
    cursor.execute('''
        CREATE TABLE post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database table 'posts' has been refreshed.")
def create_post_theme():
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_theme (
            themeid INTENGER,
            postid INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created and table 'themes' is ready.")


if __name__ == '__main__':
    create_themes()