from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
def hello():
    return render_template('hello.html')

@app.route('/ocean_workshop')
def ocean_workshop():
    return render_template('ocean_lab.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
