## SRP Project Documentation

### Project Folder Breakdown
The project of SRP is seperated into 4 folders.
1) srp_app - In this project folder, the backend is implemented in python pysrp and the javascript client library used is srp-client.js
    for the protocol security issue, please refer to readme.md file in the project folder

2) srp_app_fail - In this project folder, the backend is implemented in pysrp and the client side send the password to server and used pysrp to generate the Session key.
   1) There is a security issue for MITM in this implementation as it is not the SRP protocol at all as the password is hashed and send over to the backend.

3) srp_app_nodejs - In this project folder, the backend and frontend is implemented in node and javascript. This is the correct implementation of SRP protocol.

4) srp_app_python - In this project folder, SRP protocol is implemented in python. It is not a web app.

Note - The project folder, 1,2 and 3 can be run using python3 app.py and npm run.

### Known Security 

#### Client
1) CSRF and Header Tokens are not configured as the project is meant to demonstrate the SRP protocol. It is not meant to be used in production app. RISK( Medium (High))
2) Anticlickjacking headers are not set. (Medium(High))

#### Backend
3) For docker container scan, need to set proper user permission and project file paths.
4) For Python backend, the flask is set debug to true as it is not for production use.
5) For Python lib, there is a subprocess call with shell=True set. In production, can be set to shell = False.
