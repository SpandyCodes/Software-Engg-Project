from pythonfiles import app
from flask_mysqldb import MySQL
import MySQLdb.cursors



mysql = MySQL(app)
 
#Creating a connection cursor
cursor = mysql.connection.cursor()
 
#Executing SQL Statements
cursor.execute(''' CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    photo BLOB,
    passwrd VARCHAR(255),
    confirm_passwrd VARCHAR(255),
    DOB DATE,
    skills VARCHAR(255)
) ''')


cursor.execute('''CREATE TABLE Grp (
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    admin INT,
    FOREIGN KEY (admin) REFERENCES User(user_id),
    creation_date DATE
)''')



cursor.execute('''CREATE TABLE GroupMember (
    grpmember_id INT PRIMARY KEY AUTO_INCREMENT,
    grp_id INT,
    user_id INT,
    role VARCHAR(255),  -- Added data type for the 'role' column
    FOREIGN KEY (grp_id) REFERENCES Grp(group_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
)''')


cursor.execute(''' CREATE TABLE Task (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(1000),
    deadline DATE,
    assigned_to INT,
    FOREIGN KEY (assigned_to) REFERENCES User(user_id),
    status VARCHAR(255)
)''')


cursor.execute('''CREATE TABLE Feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender INT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Changed to DATETIME
    feedback_content TEXT,
    FOREIGN KEY (sender) REFERENCES User(user_id)
)''')


cursor.execute(''' CREATE TABLE Messages (
    msg_id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT,
    group_id INT,
    date DATETIME,  -- Changed to DATETIME
    time TIME,
    msg_content TEXT,
    FOREIGN KEY (sender_id) REFERENCES User(user_id),
    FOREIGN KEY (group_id) REFERENCES Grp(group_id)
) ''')


cursor.execute(''' CREATE TABLE Announcements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    grp_id INT,
    user_id INT,
    content TEXT,
    date DATETIME,  -- Changed to DATETIME
    FOREIGN KEY (grp_id) REFERENCES Grp(group_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
)''')


#Saving the Actions performed on the DB
mysql.connection.commit()
 
#Closing the cursor
cursor.close()