from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Matthias' } # fake user
    return render_template("index.html",
        title = 'Home',
        user = user)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
    
