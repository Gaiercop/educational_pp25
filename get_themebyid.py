import sqlite3

import sqlite3


def create_theme(title, description):
    """Adds a new theme to the database."""
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    # Generate a URL based on the title (you can customize this further)
    url = "/theme/" + title.lower().replace(" ", "-")

    cursor.execute(
        "INSERT INTO themes (title, description, url) VALUES (?, ?, ?)",
        (title, description, url)
    )
    conn.commit()
    theme_id = cursor.lastrowid  # Returns the id of the last row inserted
    conn.close()
    return theme_id


def get_theme_by_id(theme_id):
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, url FROM themes WHERE id=?", (theme_id,))
    theme = cursor.fetchone()
    conn.close()
    if theme:
        return list(theme)  # Convert the tuple to a list
    else:
        return []  # Return an empty list if no theme found


def get_all_theme_ids():
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM themes")
    theme_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return theme_ids


def get_messages_by_theme_id(theme_id):
    """Retrieves all posts for a specific theme."""
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT author, content, created_at FROM post WHERE theme_id = ? ORDER BY created_at",
        (theme_id,),
    )
    posts = cursor.fetchall()
    conn.close()
    return posts


def add_new_message(theme_id, author, content):
    """Adds a new post to the database."""
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO post (theme_id, author, content) VALUES (?, ?, ?)",
        (theme_id, author, content),
    )
    conn.commit()
    conn.close()


if __name__ == '__main__':
    theme_info = get_theme_by_id(theme_id_to_find)
