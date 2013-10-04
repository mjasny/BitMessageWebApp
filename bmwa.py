from flask import Flask
app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Matthias' } # fake user
    return render_template("index.html",
        title = 'BitMessageWebApp',
        user = user)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
    
