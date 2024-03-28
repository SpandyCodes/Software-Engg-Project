from flask import Flask, render_template, request

from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__, template_folder='templates')

app.secret_key = 'parasbhosalesecretkeycollaborationplatform'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'paras3415'
app.config['MYSQL_DB'] = 'student'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_POOL_NAME'] = 'mypool'
app.config['MYSQL_POOL_SIZE'] = 10

mysql = MySQL(app)

from app import routes

