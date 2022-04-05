# import the Flask class from the flask module
import json
import logging
from re import A, S

logging.basicConfig(
    format='%(process)d- %(lineno)d - %(levelname)s-%(message)s',level=logging.INFO)
# from srplib import long_to_bytes,bytes_to_long
# from srplib import *
import srp
import urllib.request as ur
import sqlite3
import six

from flask import Flask, render_template , request,jsonify

N = 'AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740ADBF4FF74' +'7359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A' +'436C6481F1D2B9078717461A5B9D32E688F87748544523B524B0D57D' +'5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6AF874E73' +'03CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6' +'94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F' +'9E4AFF73'


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
svr = None
verifier = None
a_hex = None
salt = None
ranb=None

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
            
            svr = srp.Verifier(username,six.b(salt),six.b(verifier),six.b(a_hex))
            s,B = svr.get_challenge()
            logging.info("s - > {} \nB - > {}".format(s,B))            
            return json.dumps({'salt':str(s.hex()),'B':str(B.hex())}), 200, {'ContentType':'application/json'} 
    else: 
        return json.dumps({'success':"No Request Data"}), 400, {'ContentType':'application/json'} 


@app.route('/authenticate',methods=['POST'])
def auth():
    if request.form:
        u = request.form.get("u")
        k = request.form.get("k")
        credential = request.form.get("credentials")
        logging.info("SC - > "+credential)
        logging.info(bytes_to_long(bytes(credential,'utf-8')))
        
                # Calculate SC Server
        Nnum = bytes_to_long(N)
        
        bb = pow(2,ranb, Nnum);
        Bval = bb + (verifier *k) % (Nnum);
        
        value = pow(verifier,u,Nnum) * pow(pow(a_hex,Nnum),Bval,Nnum)
        logging.info(value)
        
        return json.dumps({'salt':'OK'}), 200, {'ContentType':'application/json'} 

    else: 
        return json.dumps({'success':"No Request Data"}), 400, {'ContentType':'application/json'} 


def chk_conn(conn):
     try:
        conn.cursor()
        return True
     except Exception as ex:
        return False


@app.route('/debug',methods=['GET'])
def debug():
   username = 'login'
   password = 'login'
   usr = User(username,password,ng_type=NG_2048,n_hex=N,g_hex="2")
   logging.info(long_to_bytes(usr.N).hex())
   logging.info(long_to_bytes(usr.g).hex())
   logging.info(long_to_bytes(usr.k).hex())
   return json.dumps({'OK':'OK'}), 200, {'ContentType':'application/json'}


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
