from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from app import mysql
import MySQLdb.cursors
import os
import bcrypt
import re  # Import the bcrypt library
from app import app
from app.utils import get_db_connection
from datetime import date


# Bcrypt configuration
bcrypt_salt_rounds = 12


# home page route
@app.route('/')
@app.route('/home')
def home():
    logout_message = None
    if 'message' in session:
        logout_message = session.pop('message')  # Retrieve flashed message
    return render_template('home.html', logout_message=logout_message)


@app.route('/paras')
def paras():
    return render_template('paras.html')





# register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        con = get_db_connection()

        if con:
            with con.cursor() as cursor:
                # Check for existing email
                cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    flash('Email already exists. Please choose another email.', 'error')
                    return render_template('home.html')

                # Validate email format
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!', 'error',category='email')  # Add category for styling
                    return render_template('home.html')

                # Validate name format
                elif not re.match(r'[A-Za-z0-9]+', name):
                    flash('Name must contain only characters and numbers!','error', category='name')
                    return render_template('home.html')

                # Check password match
                elif password != confirm_password:
                    flash('Passwords do not match. Please try again.','error', category='password')
                    return render_template('home.html')

                else:
                    # Hash password
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    # Insert user into database
                    cursor.execute(
                        "INSERT INTO User (name, email, passwrd) VALUES (%s, %s, %s)",
                        (name, email, hashed_password)
                    )
                    con.commit()

                    # Success message and redirect
                    flash('Registration successful! You can now log in.', 'success')
                    return redirect('/login')  # Redirect to login page

        else:
            flash("Failed to establish database connection", "error")
            return render_template("home.html")

    return render_template('home.html')


# login route
def verify_password(stored_password, provided_password):
    stored_password_bytes = stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password
    return bcrypt.checkpw(provided_password, stored_password_bytes)
from flask import session




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')  # Encode the password as bytes

        con = get_db_connection()

        if con:
            with con.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user and verify_password(user['passwrd'], password):
                    # Successful login
                    session['user_id'] = user['user_id']  # Store user's id in the session
                    session['username'] = user['name']  # Store user's username in the session
                    session['email'] = user['email']  # Store user's email in the session
                    flash('Login successful!', 'success')
                    return redirect(url_for('profile'))
                else:
                    # Failed login
                    flash('Invalid email or password. Please try again.', 'error')
                    return redirect(url_for('login'))

        else:
            flash("Failed to establish database connection", "error")
            return redirect(url_for('login'))

    return render_template('login.html')




@app.route('/profile')
def profile():
    # Check if user is logged in
    if 'user_id' in session:
        # Retrieve user information from session
        username = session['username']
        email = session['email']
        # Render the profile template with user information
        return render_template('profile.html', username=username, email=email)
    else:
        # If user is not logged in, redirect to login page
        flash('Please login to access your profile.', 'error')
        return redirect(url_for('login'))




# logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))



# creategroup route 
@app.route('/create_group', methods=['POST','GET'])
def create_group():
    if request.method == 'POST':
        name=request.form['name']
        email = request.form['email']
        admin=request.form['admin']
        creation_date = date.today().strftime('%Y-%m-%d')  # Get current date in YYYY-MM-DD format


        con = get_db_connection()

        if con:
            with con.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    cursor.execute("INSERT INTO grp (name, admin, creation_date) VALUES (%s, %s, DATE('now'))", (name, admin))
                    con.commit()
                    con.close()
                    return render_template('home.html')

                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!', 'error',category='email')  # Add category for styling
                    return render_template('creategrp.html')

                else:
                    conn.close()
                    flash("Admin not registered")
                    return render_template('create_group.html')
        else:
            conn.close()
            flash("Admin not registered")
            return render_template('create_group.html')

    return render_template('creategrp.html')

                








@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/one')
def one():
    return render_template('nav.html')


  