"""
    This is the main server application for the Gateway of the Refined Smart House project.
    It serves the webpage to a user trying to enter the smart house intranet.
    If the user is not logged in, it brings them to a login page.
    Otherwise, it brings them to the control hub page.
"""

# Import necessary modules
from __future__ import print_function                                                   # Use the print function
from flask import Flask, render_template, request, redirect, session, abort, url_for    # All our Flask library files (for server-side)
from flask_session import Session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from os import urandom, environ                                                         # Used to create our secret key
import sys                                                                              # Used for error logging

app = Flask(__name__, template_folder="templates")                                      # Our server applicaton
app.secret_key = urandom(256)                                                           # Generate the random key
SESSION_TYPE = 'filesystem'
SECRET_KEY = app.secret_key 
app.config.from_object(__name__)
Session()

def generate_token(username, expiration=600):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({ 'id': username})

def validate_token(token):
    s = Serializer(app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    user = data['id']
    return user

@app.route("/")                                                 # Main page
def home():
    # if not session.get('logged_in'):                            # Check to see if we have logged in
    if 'token' not in session:
        return redirect('/html/login')                          # If not, go to the login page
    elif not validate_token(session['token']):
        return redirect('/html/login')                          # If not, go to the login page
    else:
        return redirect('http://localhost:60000')        # Otherwise, go to the control hub page

@app.route("/html/login", methods=["GET", "POST"])              # Login page
def login():
    error = None

    if request.method == 'POST':                                                                        # Post method
        if request.form['username'] != "general kenobi" or request.form['password'] != "hello there":   # Check login credentials
            error = "Username or Password is incorrect. Please try again."                              # Log credentials error
        else:
            # session['logged_in'] = True                                                                 # If login successful, set the session state
            # r = requests.post()
            response = request.form
            # session['token'] = response['username'] + str(SECRET_KEY)
            session['token'] = generate_token(response['username'])
            return home()
    return render_template("/html/login.html", error=error)                                             # Render the login page

@app.route("/logout")                   # Logout page
def logout():                       
    # session['logged_in'] = False        # Reset the users session
    session.pop('token', None)
    return home()                       # Go back home

if __name__ == '__main__':
    app.run(debug=True)        # Run the application