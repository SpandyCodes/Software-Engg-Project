from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__, template_folder='templates')

app.secret_key = 'parasbhosalesecretkeycollaborationplatform'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'paras3415'
app.config['MYSQL_DB'] = 'student'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_POOL_NAME'] = 'mypool'
app.config['MYSQL_POOL_SIZE'] = 10


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 465 
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'parasbhosale375'  # Your email username
app.config['MAIL_PASSWORD'] = 'paras@1730'  # Your email password


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USERNAME = 'parasbhosale375'
EMAIL_PASSWORD = 'paras@1730'


mail = Mail(app)

mysql = MySQL(app)

from app import routes

