from flask import Flask,render_template, request
from flask_mysqldb import MySQL
import MySQLdb.cursors

 
app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'paras3415'
app.config['MYSQL_DB'] = 'student'
 
mysql = MySQL(app)
app.app_context().push() 
from pythonfiles import route