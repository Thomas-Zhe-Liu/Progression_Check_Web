from app import app
from flask import render_template

@app.route('/')
#@app.route('/index')
@app.route('/step1')
#@app.route('/step2')
#@app.route('step3')
def index():
    #return render_template('index.html')
    return render_template('step1.html')
    #return render_template('step2.html')
    #return render_template('step3.html')
