from flask import render_template
from pythonfiles import app
from pythonfiles.model import mysql


# home page route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')




# register page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


    

# login page route
@app.route('/login')
def login():
    return render_template('login.html')
