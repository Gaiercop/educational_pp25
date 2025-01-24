from flask import Flask, render_template
from get_themebyid import *
app = Flask(__name__)
def get_all_theme_ids():
    """
    Retrieves all theme IDs from the database and returns them as a list.
    """
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM themes")
    theme_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    return theme_ids
@app.route('/')
def forum():
    theme_list = get_all_theme_ids()
    theme = []
    for i in theme_list:
        theme.append(get_theme_by_id(i))
    return render_template('forum_main.html', popular_themes = theme)
@app.route('/forum/topic/<theme_id>')
def show_theme(theme_id):
    theme_info = get_theme_by_id(theme_id)
    print(theme_info)
    return render_template('theme_page.html', theme=theme_info)

if __name__ == '__main__':
    app.run(debug=True)
