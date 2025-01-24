from flask import Flask, render_template

app = Flask(__name__)

@app.route('/catalogs')
def catalogs():
    catalogs = ['Electronics', 'Books', 'Clothing', 'Home & Garden']
    return render_template('catalogs.html', catalogs=catalogs)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
