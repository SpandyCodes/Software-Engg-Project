import pymysql

# DATABASE CONNECTION
def get_db_connection():
    try:
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='paras3415',
            database='STUDENT',
            cursorclass=pymysql.cursors.DictCursor
        )

        return con
    except Exception as e:
        print(f"Error: {e}")
        return None
