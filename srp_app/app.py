# import the Flask class from the flask module
import json
import logging
from re import S
logging.basicConfig(
    format='%(process)d- %(lineno)d - %(levelname)s-%(message)s',level=logging.INFO)
import srp
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
        dbconnection = sqlite3.connect('app.db')
        if(chk_conn(dbconnection)):
            username = request.form.get("username")
            salt = request.form.get("salt")
            verifier = request.form.get("verifier")
            logging.info("\n\n{} \n\n{} \n\n{}".format(username,salt,verifier))
            cur = dbconnection.cursor()
            cur.execute("INSERT INTO user (username, salt, verifier) VALUES (?, ?, ?)",
                        (username, salt,verifier)
                        )
            dbconnection.commit()
            dbconnection.close()
            return render_template('login.html')
        else:
            print("DB CONNECTION CLOSED")
            return render_template('register.html')
    
    
        
@app.route('/challange',methods=['POST'])
def challange():
    if request.form:
        username = request.form.get("username")
        a_hex = request.form.get("server_a")
        print(username)
        print(a_hex)
        if request.method != 'POST' or username is None or a_hex is None:
            return json.dumps({'success':"Invalid Username in Request"}), 400, {'ContentType':'application/json'} 
        else:
            dbconnection = sqlite3.connect('app.db')
            cur = dbconnection.cursor()
            cur.execute("SELECT * FROM user WHERE username = ?",(username,))
            rows = cur.fetchall()
            for row in rows:
                salt = row[2]
                verifier = row[3]
            dbconnection.close()
            
            print("A : {}".format(a_hex))
            print("Username : {}".format(username))
            print("Salt : {}".format(salt))
            print("Verifer : {}".format(verifier))
            
            svr = srp.Verifier( str(username), bytes(salt,encoding='utf8'), bytes(verifier,encoding='utf8'), bytes(a_hex,encoding='utf8'))
            s,B = svr.get_challenge()
            logging.info("\nuname -> {}\nA -> {}".format(str(s.hex()),str(B.hex())))
            
            if s is None or B is None:
                logging.error ("Auth Failed.")
                return
            logging.info("\nuname -> {}\nA -> {}".format(str(s.hex()),str(B.hex())))
            return json.dumps({'salt':str(salt),"B":str(B)}), 200, {'ContentType':'application/json'} 

    else: 
        return json.dumps({'success':"No Request Data"}), 400, {'ContentType':'application/json'} 


def chk_conn(conn):
     try:
        conn.cursor()
        return True
     except Exception as ex:
        return False
    
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
