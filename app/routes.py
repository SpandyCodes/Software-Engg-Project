from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from flask_mail import Mail, Message
from app import mysql,mail
import MySQLdb.cursors
import os
import bcrypt
import re  # Import the bcrypt library
from app import app
from app.utils import get_db_connection
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from werkzeug.utils import secure_filename

filename = "my&file.txt"
secure_filename(filename)  # Returns: "my_file.txt"


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
                    flash('Invalid email address!', 'error',category='email') 
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
                    return redirect(url_for('home'))

        else:
            flash("Failed to establish database connection", "error")
            return redirect(url_for('login'))

    return render_template('home.html')





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
        return redirect(url_for('home'))
    
    

# Define allowed file extensions for photo upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}




# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# Function to hash the password
def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')  # Decode bytes to string for storage in the database



@app.route('/update_profile', methods=['POST','GET'])
def update_profile():
    username = session['username']
    email=session['email']

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        dob = request.form['dob']
        skills = request.form['skills']
        photo = request.files['photo']


        if not name or not email:
             # Validate form data
            flash("Name and email are required fields.", 'error')
            return redirect(url_for('profile'))


# Password validation
        if password:
            if password != confirm_password:
                flash("Passwords do not match.", 'error')
                return redirect(url_for('profile'))


        # Update user profile in the database
        con = get_db_connection()
        if con:
            with con.cursor() as cursor:
                # Update the user's name and email
                cursor.execute("UPDATE user SET name = %s, email = %s WHERE name = %s", (name, email, username))

                # Update password if provided
                if password:
                    hashed_password = hash_password(password)
                    cursor.execute("UPDATE user SET password = %s WHERE name = %s", (hashed_password, username))

                # Update date of birth
                if dob:
                    cursor.execute("UPDATE user SET dob = %s WHERE name = %s", (dob, username))


            # Update skills
                if skills:
                    cursor.execute("UPDATE user SET skills = %s WHERE name = %s", (skills, username))
                

                # Handle photo upload
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    # photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    # photo.save(photo_path)
                    cursor.execute("UPDATE user SET photo_path = %s WHERE name = %s", (photo_path, username))

                    cursor.execute("UPDATE config SET upload_folder = %s WHERE id = 1", (app.config['UPLOAD_FOLDER'],))


                   
                con.commit()
                flash("Profile updated successfully.", 'success')
                con.close()
                return redirect(url_for('profile'))

        else:
            flash("Database connection error", 'error') 
    
    return render_template('update_profile.html',username=username,email=email)
                     
                




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

    if 'user_id' not in session:
        flash("You need to log in to create a group.", 'error')
        return redirect(url_for('create_group'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        admin_name = request.form['admin']
        creation_date = date.today().strftime('%Y-%m-%d')  # Get current date in YYYY-MM-DD format

        con = get_db_connection()

        if con:
            with con.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
                user = cursor.fetchone()

                cursor.execute("SELECT group_id FROM grp WHERE name = %s AND admin_name = %s", (name, admin_name))
                existing_group = cursor.fetchone()

                if existing_group:
                    con.close()
                    flash("Group with the same name and admin already exists.",'error')
                    return redirect(url_for('create_group'))

                if user:
                    # Insert new group into grp table
                    cursor.execute("INSERT INTO grp (name, admin_name, creation_date) VALUES (%s, %s, %s)",
                                   (name, admin_name, creation_date))
                    con.commit()

                    # # Get the group ID of the newly created group
                    # cursor.execute("SELECT LAST_INSERT_ID()")
                    # group_id = cursor.fetchone()[0]

                    # Insert admin into groupmember table
                    cursor.execute("INSERT INTO groupmember (group_name, username) VALUES (%s, %s)",
                                   (name, admin_name))
                    con.commit()

                    con.close()
                    flash("Group is Created", 'success')
                    return redirect(url_for('profile'))

                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!', 'error')  # Add category for styling
                    return redirect(url_for('/create_group'))

                else:
                    con.close()
                    flash("Admin not registered",'error')
                    return redirect(url_for('create_group'))
        else:
            conn.close()
            flash("Admin not registered",'error')
            return redirect(url_for('create_group'))

    return render_template('creategrp.html')

                







#CONTACT ROUTE
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not (name and email and message):
            flash('Please fill in all fields.', 'error')
            return redirect(request.url)

        msg = Message(subject='Contact Form Submission',
                      sender=email,
                      recipients=['bhosaleparas030@gmail.com'],  # Your email address
                      body=f'Name: {name}\nEmail: {email}\nMessage: {message}')

        try:
            mail.send(msg)
            flash('Your message has been sent successfully.', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {str(e)}', 'error')

        return redirect(url_for('profile'))

    # If the request method is GET, render the contact form template
    return render_template('contact.html')





#to do list
@app.route('/todo', methods=['POST','GET'])
def todo():
    user_name = session['username']
    task=None
    if request.method == 'POST':
        task = request.form['task']  # Get the task from the form

        con = get_db_connection()

        if con:
            cursor = con.cursor()
            # Insert the user's name and to-do list into the database
            insert_query = "INSERT INTO todo (user_name, todo_list) VALUES (%s, %s)"
            cursor.execute(insert_query, (user_name, task))
            con.commit()
            con.close()
            flash("To do List stored Successfully")
            return redirect(url_for('profile'))

        else:
            flash('Database connection failed', 500)
            return redirect(url_for('profile'))

    return render_template('index.html')


    

 # SEE PRVIOUS LIST
@app.route('/previous_lists', methods=['GET'])
def previous_lists():
    user_name = session.get('username')
    user_email = session.get('email')  # Assuming you store user's email in session

    if not user_name:
        flash('User not logged in', 'error')
        return redirect(url_for('login'))

    con = get_db_connection()

    if con:
        cursor = con.cursor()

        # Retrieve previous to-do lists from the database
        select_query = "SELECT todo_list FROM todo WHERE user_name = %s"
        cursor.execute(select_query, (user_name,))
        previous_lists = cursor.fetchall()
        print(previous_lists)

        con.close()

        # Send email notification with previous to-do lists
        if previous_lists:
            todo_message = "\n".join(f"- {todo['todo_list']}" for todo in previous_lists)
            send_todo_list_email(user_email, user_name, todo_message)

        # Render HTML template and pass previous lists data to it
        return render_template('previous_lists.html', previous_lists=previous_lists, username=user_name)
    else:
        flash('Database connection failed', 'error')
        return redirect(url_for('profile'))

def send_todo_list_email(recipient_email, username, todo_message):
    try:
        msg = Message(subject='Your Previous To-Do Lists',
                      sender='your_email@example.com',  # Your email address
                      recipients=[recipient_email],
                      body=f'Hello {username},\n\nHere are your previous to-do lists:\n\n{todo_message}\n\nBest regards,\nYour Application Team')

        mail.send(msg)
        flash('Email notification sent successfully', 'success')
    except Exception as e:
        flash(f'An error occurred while sending email notification: {str(e)}', 'error')


# DELETE TO DO LIST TASK
@app.route('/complete_task/<task>', methods=['GET'])
def complete_task(task):
    user_name = session.get('username')
    if not user_name:
        flash("User not logged in", 'error')
        return redirect(url_for('login'))

    con = get_db_connection()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute("DELETE FROM todo WHERE user_name = %s AND todo_list = %s", (user_name, task))
            con.commit()
            con.close()
            flash("Task completed successfully",'success')
            return redirect(url_for('previous_lists'))
        except Exception as e:
            flash("An error occurred while completing the task", 'error')
    else:
        flash("Database connection failed", 'error')

    return redirect(url_for('previous_lists'))
    




# showing my groups
@app.route('/my_groups')
def my_groups():
    if 'username' not in session:
        flash("You need to log in to view your groups.", 'error')
        return redirect(url_for('login'))

    username = session['username']

    con = get_db_connection()

    if con:
        with con.cursor() as cursor:
            cursor.execute("SELECT group_name FROM groupmember WHERE username = %s", (username,))
            groups = cursor.fetchall()
            groups = [group['group_name'] for group in groups]  
            con.close()
            return render_template('test1.html', groups=groups)
    else:
        flash("Database connection error", 'error')
        return redirect(url_for('profile'))
