# import the Flask class from the flask module

import logging
logging.basicConfig(
    format='%(process)d- %(lineno)d - %(levelname)s-%(message)s',level=logging.INFO)
import srp
import sqlite3
from flask import Flask, render_template, request

# create the application object
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('login.html')  # return a string

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
            password = request.form.get('password')
            salt, vkey = srp.create_salted_verification_key( username, password )

            logging.info(f"\n\n{username} \n\n{salt} \n\n{vkey}")
            
            cur = dbconnection.cursor()
            cur.execute("INSERT INTO user (username, salt, verifier) VALUES (?, ?, ?)",
                        (username, salt, vkey)
                        )
            dbconnection.commit()
            dbconnection.close()
            return render_template('login.html')
        else:
            print("DB CONNECTION CLOSED")
            return render_template('register.html')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if request.form:

        username = request.form.get("username")
        password = request.form.get("password")

        user = srp.User( username, password )
        uname, A = user.start_authentication()

        salt, vkey = get_creds_from_db(uname)
        svr = srp.Verifier( uname, salt, vkey, A )
        s,B = svr.get_challenge()

        if s is None or B is None:
            logging.error("Auth Failed")
            render_template('index.html', message='User Not Authorized')
        
        M = user.process_challenge( s, B )

        if M is None:
            logging.error("Auth Failed")
            render_template('index.html', message='User Not Authorized')

        HAMK = svr.verify_session( M )

        if HAMK is None:
            logging.error("Auth Failed")
            render_template('index.html', message='User Not Authorized')

        user.verify_session( HAMK )

        if user.authenticated() and svr.authenticated():
            return render_template('index.html', name=username)
        
    return render_template('index.html', message='User Not Authorized')


def get_creds_from_db(uname):
    dbconnection = sqlite3.connect('app.db')
    cur = dbconnection.cursor()
    cur.execute("SELECT salt, verifier FROM user WHERE username = ?", (uname,))
    row = cur.fetchone()
    salt, verifier = row
    dbconnection.close()

    return salt, verifier

def chk_conn(conn):
     try:
        conn.cursor()
        return True
     except Exception as ex:
        return False
    
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
