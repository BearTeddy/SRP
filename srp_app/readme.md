srp-app
=====

Purpose of this folder
----------------------
In this project folder, the backend is implemented in pysrp and the javascript client library used is srp-client.js

#####Note - Refer to SRP protocol in main ReadMe.

The issue with project folder is that the Hashing function used in srp-client.js and pysrp is different.
As H() is One-way hash function, as long as the hashing used in front end and back end is the same and used RFC5054 as a standard, it should work.

This is the correct implementation of the SRP-6.

The Session Key turns out different in this project.
### Can Simulate By Following setup.

    1.) run the app.py using python. will be hosted in localhost:5000 as default
    2.) go to localhost:5000/register and register using username and password.
    3.) Open the console of the browser. the secret and verifer will be logged in console log.
    4.) Try to login with the username and password in localhost:5000/login
    5.) In the console log, there will be two value logged. Session key from client side calcuation and Session key from server side calculation which has to be the same.

For Correct implementation and usage of js library, refer to https://github.com/symeapp/srp-client 

    
    