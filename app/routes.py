from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from flask import jsonify
from flask_mail import Mail, Message
from app import mysql,mail
import MySQLdb.cursors
import os
import bcrypt
import re  # Import the bcrypt library
from app import app,socketio
from app.utils import get_db_connection
from datetime import date,timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

from flask_socketio import SocketIO, join_room, leave_room, emit

from datetime import datetime

from email.mime.multipart import MIMEMultipart
import smtplib
# Built-in Imports

import os

from datetime import datetime

from base64 import b64encode

import base64

from io import BytesIO

filename = "my&file.txt"
secure_filename(filename)  # Returns: "my_file.txt"


# Bcrypt configuration
bcrypt_salt_rounds = 12




# home page route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')




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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




# Function to hash the password
def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')  # Decode bytes to string for storage in the database


# UPDATE PROFILE
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
                    cursor.execute("UPDATE user SET passwrd = %s WHERE name = %s", (hashed_password, username))

                # Update date of birth
                if dob:
                    cursor.execute("UPDATE user SET dob = %s WHERE name = %s", (dob, username))


            # Update skills
                if skills:
                    cursor.execute("UPDATE user SET skills = %s WHERE name = %s", (skills, username))
                

                # Handle photo upload
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    # Establish database connection (assuming get_db_connection() returns a connection)

                    con = get_db_connection()

                    if con:

                        with con.cursor() as cursor:

                            # Save the uploaded file

                            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                            photo.save(photo_path)

                            print(f"Saving photo to: {photo_path}")

                            # Update user's photo path in the database

                            cursor.execute("UPDATE user SET photo_path = %s WHERE name = %s", (photo_path, username))

                            con.commit()

                        con.close()

                        flash("Profile updated successfully.", 'success')

                        return redirect(url_for('profile'))

                    

                    else:

                        flash("Database connection error", 'error')

                        return redirect(url_for('profile'))
                   
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
    flash('Logged out successfully!', 'warning')
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
                    flash("Group with the same name and admin already exists.", 'error')
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
                    flash("Admin not registered", 'error')
                    return redirect(url_for('create_group'))
        else:
            conn.close()
            flash("Admin not registered", 'error')
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

        

        # Render HTML template and pass previous lists data to it
        return render_template('previous_lists.html', previous_lists=previous_lists, username=user_name)
    else:
        flash('Database connection failed', 'error')
        return redirect(url_for('profile'))

# EMAIL todo

def send_todo_list_email(user_email, user_name, todo_message):

    """Sends an email notification containing the user's to-do list.



    Args:

        user_email (str): User's email address.

        user_name (str): User's name.

        todo_message (str): User's to-do list message.



    Returns:

        bool: True if email sent successfully, False otherwise.

    """
    try:
        msg = MIMEMultipart()  # Create a multipart email message
        # Set email headers:

        msg['From'] = 'parasbhosale375@gmail.com'  # Replace with your actual email address

        msg['To'] =' parasbhosale184@gmail.com'

        msg['Subject'] = 'Your To-Do List'



        # Create the email body as plain text:

        body = f'Hello {user_name},\n\nHere is your to-do list:\n\n{todo_message}\n\nBest regards,\nYour Application Team'

        msg.attach(MIMEText(body, 'plain'))  # Attach body as plain text



       

        with smtplib.SMTP('smtp.gmail.com', 465) as server:

            server.starttls()

            server.login('parasbhosale375@gmail.com', 'paras@1730')  # Replace with your email credentials

            server.sendmail('parasbhosale375@gmail.com', ' parasbhosale184@gmail.com', msg.as_string())

        return True
    except Exception as e:
        print(f'An error occurred while sending email notification: {str(e)}')

        return False



    return True  # Assuming successful email sending with your implementation





# Function to schedule sending email at specific date and time (remains unchanged)

def schedule_email_at_datetime(user_email, user_name, todo_message, datetime_obj):

    scheduler.add_job(send_todo_list_email, 'date', run_date=datetime_obj, args=[user_email, user_name, todo_message])





# Rest of your code (including schedule_email function and template) can remain similar





@app.route('/schedule_email', methods=['POST'])

def schedule_email():

    # user_email = session['email']  # Retrieve user's email from session

    user_name = session['username'] # Retrieve user's name from session

    user_email=None



    if not user_email:

        flash('User not logged in', 'error')

        return redirect(url_for('profile'))

    

    con = get_db_connection()

    previous_lists=None



    if con:

        cursor = con.cursor()



        # Retrieve previous to-do lists from the database

        select_query = "SELECT todo_list FROM todo WHERE user_name = %s"

        cursor.execute(select_query, (user_name,))

        previous_lists = cursor.fetchall()

        print(previous_lists)



        select_query = "SELECT email FROM user WHERE user_name = %s"

        cursor.execute(select_query, (user_name,))

        user_email = cursor.fetchone()



        con.close()



    todo_message = previous_lists  # Retrieve to-do list from session or wherever it's stored



    if not todo_message:

        flash('No to-do list found', 'error')

        return redirect(url_for('profile'))



    # Parse date and time from form input

    date = request.form.get('date')

    time = request.form.get('time')

    am_pm = request.form.get('am_pm')



    if not (date and time and am_pm):

        flash('Please provide both date and time', 'error')

        return redirect(url_for('previous_lists'))



    # Combine date and time strings

    datetime_str = f"{date} {time} {am_pm}"



    # Parse datetime string into a datetime object

    try:

        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %I:%M %p')

    except ValueError:

        flash('Invalid date and time format', 'error')

        return redirect(url_for('previous_lists'))



    # Schedule sending email at the specified datetime

    schedule_email_at_datetime(user_email, user_name, todo_message, datetime_obj)



    return redirect(url_for('profile'))


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
            return render_template('my_group.html', groups=groups,user_name=username)
    else:
        flash("Database connection error", 'error')
        return redirect(url_for('profile'))











# ADDING GROUP MEMBERS TO GROUP

@app.route('/add_member', methods=['POST','GET'])

def add_member():

    if request.method == 'POST':

        group_name = request.form['group_name']

        username = request.form['username']

        email = request.form['email']



        con = get_db_connection()



        if con:

            cursor = con.cursor()

            # Check if the user exists in the database

            cursor.execute("SELECT user_id FROM user WHERE name = %s AND email = %s", (username, email))

            user_result = cursor.fetchone()

            print(user_result)



            if user_result is None:

                flash('User does not exist. Please check the name and email.', 'error')

                return redirect(url_for('my_groups'))  # Redirect to the homepage or wherever you want



            cursor.execute("SELECT grpmember_id FROM groupmember WHERE group_name = %s", (group_name))

            group_result = cursor.fetchone()



            if group_result is None:

                flash('Group does not exist.', 'error')

                return redirect(url_for('my_groups'))  # Redirect to the homepage or wherever you want





            # Check if the user is already a member of the group

            cursor.execute("SELECT grpmember_id FROM groupmember WHERE  group_name = %s AND email = %s", (group_name, email))

            group_member_result = cursor.fetchone()



            if group_member_result:

                flash('User is already a member of the group.', 'info')



            else:

                # Add the user to the group

                cursor.execute("INSERT INTO groupmember (username, group_name,email) VALUES (%s, %s ,%s )",

                (username,group_name,email))

                con.commit()

                flash('User added to the group successfully.', 'success')



        return redirect(url_for('my_groups'))  # Redirect to the homepage or wherever you want



    return redirect(url_for('my_groups'))



   

    

    







# VIEW GROUP MEMBERS

@app.route('/view_members', methods=['GET', 'POST'])

def view_members():



    username=session['username']

    if request.method == 'POST':

        group_name = request.form['group_name']



        con = get_db_connection()



        if con:

            cursor = con.cursor()



            cursor.execute("SELECT group_name FROM groupmember WHERE username = %s", (username,))

            groups = cursor.fetchall()

            groups = [group['group_name'] for group in groups]  



            query = "SELECT username,email FROM groupmember WHERE group_name = %s"

            cursor.execute(query, (group_name,))

            members = cursor.fetchall()

            print(members)



            return render_template('members.html', group_name=group_name, members=members,groups=groups,username=username)



    return render_template('my_group.html')











# ASSIGN TASK

@app.route('/assign_task', methods=['POST', 'GET'])

def assign_task():

    user_name = session['username']

    print(user_name)



    # Fetching groups

    con = get_db_connection()

    groupes = []

    if con:

        cursor = con.cursor()

        cursor.execute("SELECT group_name FROM groupmember WHERE username = %s", (user_name,))

        groups_data = cursor.fetchall()

        groupes = [group['group_name'] for group in groups_data]



    if request.method == 'POST':

        # Get form data

        title = request.form['taskTitle']

        description = request.form['taskDescription']

        group = request.form['selectGroup']

        user = request.form['selectUser']

        due_date = request.form['dueDate']

        status = request.form['taskStatus']





        con = get_db_connection()



        if con:

            cursor = con.cursor()

            

            # Insert task into the database

            cursor.execute("SELECT user_id FROM user WHERE name = %s", (user,)) 

            owner_id = cursor.fetchone()['user_id']



            cursor.execute("SELECT name FROM user WHERE name = %s", (user_name,)) 

            owner = cursor.fetchone()['name']



            cursor.execute("SELECT admin_name FROM grp WHERE name = %s", (group,))

            group_name = cursor.fetchone()['admin_name']



            if owner==group_name:

                cursor.execute("INSERT INTO task (task_name, description, group_name, assigned_to, deadline, status,assigned_user) VALUES (%s, %s, %s, %s, %s, %s,%s)",(title, description, group, owner_id, due_date, status,user))

                con.commit()

                flash('Task assigned successfully!', 'success')

                return redirect(url_for('assign_task'))  # Redirect to the same route after successful form submission

            else:

                flash("You are not admin ",'error')

                return redirect(url_for('assign_task'))



        else:

            flash('Task Not Assigned', 'errors')

            return redirect(url_for('assign_task'))



    # con.close()  # Close the connection here if it wasn't closed in the 'if con:' block above



    return render_template('assign_task.html', groupes=groupes)





            





# Function to fetch users from the database based on selected group

def fetch_users_from_database(selected_group):

    # Establish a connection to the database

    conn=get_db_connection()

    cursor = conn.cursor()

    try:



        cursor.execute("SELECT username FROM groupmember WHERE group_name= %s",(selected_group))

        

        # Fetch all users and return as a list of dictionaries

        users = cursor.fetchall()

        print(users)

        return users



    except  Exception as e:

         conn.rollback()

         return []



    finally:

        conn.close()



     



# Define route to fetch users based on selected group

@app.route('/get_users', methods=['POST', 'GET'])

def get_users():

  selected_group = request.args.get('group')



  users = fetch_users_from_database(selected_group)  # Call function to fetch users

  print(users)



  # Ensure users is a list and contains username information

  if not users or not all(user.get('username') for user in users):

    return jsonify([]), 404  # Return empty list with 404 Not Found if no users found



  return jsonify(users)  # Return list of users with username property



        









# 6f07bf







# TASK HISTORY

@app.route('/task_hist', methods=['POST', 'GET'])

def task_hist():

    groupes = []

    user_name = session['username']

    con = get_db_connection()



    groupName=None    

    task_data=[]

    count=10





    if con:

        cursor = con.cursor()

        cursor.execute("SELECT group_name FROM groupmember WHERE username = %s", (user_name,))

        groups_data = cursor.fetchall()

        groupes = [group['group_name'] for group in groups_data]





    if request.method == 'POST':

        groupName =request.form['groupName']  # Ensure form field name is 'groupName'



        if con:

            cursor = con.cursor()





            # cursor.execute("SELECT group_name FROM grp WHERE group_name = %s", (groupName))

            # Check if the logged-in user is a member of the specified group

            cursor.execute("SELECT username FROM groupmember WHERE group_name = %s", (groupName,))

            users_in_group = cursor.fetchall()

            users_in_group = [user['username'] for user in users_in_group]



            if user_name in users_in_group:

                # If the user is a member of the group, retrieve task data for that group

                cursor.execute("SELECT task_name, assigned_user, deadline, status, group_name FROM task WHERE group_name = %s", (groupName,))

                task_data = cursor.fetchall()

                cursor.close()

                con.close() 

                return render_template('task_history.html', group_name=groupName, groupes=groupes, username=user_name, task_data=task_data, count=count)

            else:

            # If the user is not a member of the group, redirect them to 'my_groups' page

               flash("You are not a member of " + groupName + " Group", 'error')

               return redirect(url_for('my_groups'))



    # Render the template without any data if the request method is GET or if there was an error

    return render_template('task_history.html',group_name=groupName,groupes=groupes,username=user_name,task_data=task_data)







# SEE MY TASKS

@app.route('/my_tasks')

def my_tasks():

    username=session['username']



    con = get_db_connection()



    if con:

        cursor=con.cursor()

        cursor.execute('SELECT * from task WHERE assigned_user = %s', (username,))

        tasks = cursor.fetchall()

        print(tasks)

        cursor.close()

        return render_template('my_tasks.html', tasks=tasks)





    return render_template('my_tasks.html', tasks=[])







# UPDATE TASK

@app.route('/update_task_status', methods=['POST', 'GET'])

def update_task_status():

    user_name=session['username']

    if request.method=='POST':

        task_identifier = request.form['task_identifier']  # Assuming task name is sent as form data

        new_status = request.form['new_status']

        assigned_user=request.form['assigned_user']

        group_name=request.form['group_name']



        con = get_db_connection()

        if con:

            cursor = con.cursor()

            cursor.execute('SELECT group_name from task WHERE task_name = %s AND assigned_user = %s', (task_identifier, assigned_user))

            grp_name=cursor.fetchone()

            print(grp_name['group_name'])

            print(group_name)



            if group_name==grp_name['group_name']:

                # Update the status and assinged user of the task

                

                cursor.execute("UPDATE task SET status=%s WHERE task_name=%s AND assigned_user=%s", (new_status, task_identifier,assigned_user ))

                con.commit()  # Commit the transaction

                con.close()   # Close the database connection



                flash("status updated successfully",'success')

                return redirect(url_for('my_groups'))

            else:

                flash("This task is not Yours",'error')

                return redirect(url_for('my_groups'))



        else:

            flash('Unable to update this time','error')

            return redirect(url_for('my_groups'))



    return render_template('task_history.html')



            

           











# TASK DETAIL

@app.route('/get_details', methods=['POST', 'GET'])

def get_details():

    if request.method == 'POST':

        assigned_user = request.json.get('assigned_user')

        task_name = request.json.get('task_name')



        con = get_db_connection()

        details = None

        if con:

            cursor = con.cursor()

            cursor.execute('SELECT description from task WHERE task_name = %s AND assigned_user = %s', (task_name, assigned_user))

            row = cursor.fetchone()

            if row:

                details = row['description']

                # details=details['description']

                print(details)

                x=len(row)

                print(x)

                

            cursor.close()

            con.close()

            

        if details:

            return jsonify({'description':details})

        else:

            return jsonify({'message': 'Task details not found'}), 404



    return jsonify({'error': 'Invalid request'}), 400







@app.route('/chat/<group_name>')

def chat(group_name):

    # username=session['username']

    username=session['username']

    """Renders the chat template and passes the group name for dynamic functionality."""

    return render_template('chat.html', group=group_name,username=username)







# @socketio.on('message')

# def handle_message(message):

#     print("Received message: " + message)

#     # print(gr/oup)

#     if message != "User connected":

#         socketio.emit('message', message)

#         insert(message)





@socketio.on('message')

def handle_message(message):

    print("Received message: " + message)

    if message != "User connected":

        # Emit the message to the clients

        socketio.emit('message', message)

        # username = message['username']

        # message_content = message['message']

        # group = message['group']



        # Extract username from request (you may need to modify this depending on how you handle user authentication)

        username = request.args.get('username')

        print(username)

        # print(group)

        # Get the current timestamp

        timestamp = datetime.now()



        # Insert message into the database

        insert_into_database(username, message, timestamp)





def insert_into_database(username, message, timestamp):



    con = get_db_connection()



    if con:

            cursor=con.cursor()

            # Define the SQL query to insert data into the database

            sql_query = "INSERT INTO messages (username, msg_content, time) VALUES (%s, %s, %s)"

            # Execute the SQL query with the provided data

            cursor.execute(sql_query, (username, message, timestamp))



            # Commit the transaction to save the changes

            con.commit()



            # Close the cursor and connection

            con.close()

            print("Data inserted successfully into the database.")





   

@app.route('/get_username')

def get_username():

    # Retrieve the username from the session or database

    username = session['username']  # Example: Get username from session

    return jsonify({'username': username})





@app.route('/upload_file', methods=['POST'])

def upload_file():

    if 'file' not in request.files:

        return 'No file part'



    if request.method=='POST':

        file = request.files['file']

        if file.filename == '':

            return 'No selected file'

            



        upload_folder = os.path.join('D:', 'SEM 6')

        file.save(os.path.join(upload_folder, file.filename))



    return render_template('my_groups.html')



   

    



    # Construct the file path using os.path.join()

   



   