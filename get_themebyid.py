import sqlite3

def get_theme_by_id(theme_id):
    """
    Retrieves a theme from the database based on its ID and returns it as a list.
    If no theme is found, returns an empty list.
    """
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, description, url FROM themes WHERE id=?", (theme_id,))
    theme = cursor.fetchone()

    conn.close()

    if theme:
        return list(theme)  # Convert the tuple to a list
    else:
        return []  # Return an empty list if no theme found

if __name__ == '__main__':

    theme_info = get_theme_by_id(theme_id_to_find)
