# import the Flask class from the flask module
import json
import logging
from re import S
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "app.db")

logging.basicConfig(
    format='%(process)d- %(lineno)d - %(levelname)s-%(message)s',level=logging.INFO)
import srp
srp.rfc5054_enable()
import six
import urllib.request as ur
import sqlite3


from flask import Flask, render_template , request

# create the application object
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# use decorators to link the function to a url
@app.route('/')
def home():
    return "Hello, World!"  # return a string

@app.route('/index')
def welcome():
    return render_template('index.html')  # render a template

@app.route('/login',methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')  # render a template

@app.route('/save', methods=['POST'])
def saveUser():
    if request.form:
        with sqlite3.connect(db_path) as dbconnection:
            if(chk_conn(dbconnection)):
                username = request.form.get("username")
                # print(type(username))
                salt = request.form.get("salt")
                # print(type(salt))
                verifier = request.form.get("verifier")
                verifier = long_to_bytes(int(verifier)).hex()
                # print(type(verifier))
                logging.info("\n\n{} \n\n{} \n\n{}".format(username,salt,str(verifier)))
                cur = dbconnection.cursor()
                cur.execute("INSERT INTO user (username, salt, verifier) VALUES (?, ?, ?)",
                            (username, salt,str(verifier))
                            )
                dbconnection.commit()
                # dbconnection.close()
                return render_template('login.html')
            else:
                print("DB CONNECTION CLOSED")
                return render_template('register.html')

@app.route('/challange',methods=['POST'])
def challange():
    if request.json:
        # print(request.json)
        username = request.json["username"]
        a_hex = request.json["A"]
        a_hex = int(a_hex)
        # print(username)
        # print(a_hex)
        if request.method != 'POST' or username is None or a_hex is None:
            return json.dumps({'success':"Invalid Username in Request"}), 400, {'ContentType':'application/json'} 
        else:
            with sqlite3.connect(db_path) as dbconnection:
                cur = dbconnection.cursor()
                cur.execute("SELECT * FROM user WHERE username = ?",(username,))
                rows = cur.fetchall()
                print(rows)
                salt, verifier = None, None
                for row in rows:
                    salt = int(row[1], 16)
                    verifier = int(row[2], 16)
                # dbconnection.close()
                
                print("A : {}".format(a_hex))
                print(type(a_hex))
                print("Username : {}".format(username))
                print("Salt : {}".format(salt))
                print("Verifer : {}".format(verifier))
                svr = srp.Verifier( str(username), long_to_bytes(salt),long_to_bytes(verifier), long_to_bytes(a_hex))
                s,B = svr.get_challenge()
                if s is None or B is None:
                    logging.error ("Auth Failed.")
                    return
                logging.info("SVR-M : " + str(svr.M.hex()))
                logging.info("SVR-S : " + str(svr.S))
                logging.info("SVR-K : " + str(svr.K))
                
                return json.dumps({'salt':str(salt),"B":str(B.hex()).strip(),"verifier":str(verifier)}), 200, {'ContentType':'application/json'} 

    else: 
        return json.dumps({'success':"No Request Data"}), 400, {'ContentType':'application/json'} 


@app.route('/authenticate',methods=['POST'])
def authenticate():
    if request.form:
        username = request.form.get("username")


def chk_conn(conn):
     try:
        conn.cursor()
        return True
     except Exception as ex:
        return False

def bytes_to_long(s):
    n = 0
    for b in six.iterbytes(s):
        n = (n << 8) | b
    return n


def long_to_bytes(n):
    l = list()
    x = 0
    off = 0
    while x != n:
        b = (n >> off) & 0xFF
        l.append( chr(b) )
        x = x | (b << off)
        off += 8
    l.reverse()
    return six.b(''.join(l))

    
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
