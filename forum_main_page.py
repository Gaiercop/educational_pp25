from flask import Flask, render_template, request, redirect, url_for
from get_themebyid import *
app = Flask(__name__)
@app.route('/forum')
def forum():
    theme_list = get_all_theme_ids()
    theme = []
    for i in theme_list:
        theme.append(get_theme_by_id(i))
    return render_template('forum_main.html', popular_themes = theme)
@app.route('/forum/new_post', methods=['GET', 'POST'])
def do_post():
     if request.method == 'POST':
         title = request.form['title']
         description = request.form['description']
         theme_id = create_theme(title, description)
         return redirect(url_for("show_theme", theme_id = theme_id))
     return render_template('create_post.html') # Render create theme form

@app.route('/forum/topic/<theme_id>', methods = ['GET', 'POST'])
def show_theme(theme_id):
    if request.method == 'POST':
        au = request.form['author']
        cont = request.form['content']
        add_new_message(theme_id, au, cont)
    theme = get_theme_by_id(theme_id)
    posts = get_messages_by_theme_id(theme_id)
    return render_template('theme_page.html', theme=theme, posts = posts)
if __name__ == '__main__':
    app.run(debug=True)
