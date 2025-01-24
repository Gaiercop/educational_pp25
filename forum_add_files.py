from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def forum():
    theme = [1,2]
    return render_template('forum_main.html', popular_themes = theme)

if __name__ == '__main__':
    app.run(debug=True)
