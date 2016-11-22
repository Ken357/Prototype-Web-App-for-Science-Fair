# project imports
from __future__ import print_function
import os
import sys
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, advertisements, organized_searches, Adress
from flask import session as login_session
import random, string
import json
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/test/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
APP_ROOT =os.path.dirname(os.path.abspath(__file__))
# DB connection
engine = create_engine('sqlite:///prototype.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Home

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/")
@app.route("/home")
def home():
    """
        Grant access to the home page and creates new session state for security reasons.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('home.html', state=state)


# login request handler
@app.route("/login/ajax", methods=["POST"])
def login():
    """
        Handles the client's ajax login request
    """
    try:
        # Check current session state
        login_state = request.args.get('state')
        print(login_state, file=sys.stderr)
        assert login_state == login_session['state']
    except:
        raise Exception("State Error")
    try:
        # Check if the user exists and has the correct credentials
        credentials = request.data
        data = json.loads(credentials)
        print(data['username'] + " " + data['password'])
        print(session.query(Users).filter_by(username=data['username']).count(), file=sys.stderr)
        # Test1: Check if user exists
        assert session.query(Users).filter_by(username=data['username']).count() == 1
        user = session.query(Users).filter_by(username=data['username']).one()
        print(data['password'] + " " + user.password, file=sys.stderr)
        # Test2: Check if user input the right password
        assert user.password == data['password']
        print('Authentification Complete; Sending JSON Data', file=sys.stderr)
        login_session['login_bool'] = True
        # Data to send to the client in form of JSON
        data_to_save = {
            "username": user.username,
            "name": user.name,
            "id": user.id,
            "email": user.email
        }
        # Save the current user in the session and return its information to the client
        login_session['current_user'] = data_to_save
        return jsonify(user.JsonReturn)
    except:
        print('Authentification error', file=sys.stderr)
        raise Exception("Authentification Error")


# checking current session
@app.route('/session_check', methods=['GET'])
def session_check():
    """
        when the home page or profile is loaded it will check whether a user is
        logged in or not
    """
    print(login_session['current_user'], file=sys.stderr)
    try:
        # Test and check if the state argument passed to the url is the current session state
        state = request.args.get('state')
        assert state == login_session['state']
    except:
        print("I Am in state exeption", file=sys.stderr)
        raise Exception('Session key inputed is not equal to current key')
    try:
        if login_session['current_user']:
            if login_session['login_bool']:
                data_to_send = {
                    "username": login_session['current_user']['username'],
                    "email": login_session['current_user']['email'],
                    "id": login_session['current_user']['id'],
                    "bool": True
                }
                return jsonify(data_to_send)
            else:
                print("I am inside second if", file=sys.stderr)
                raise Exception()
        else:
            print("I am inside first if", file=sys.stderr)
            raise Exception()
    except:
        print("There is no current user key", file=sys.stderr)


# profile template
@app.route('/profile')
def profile():
    """
        This url will be done and handled in the server and not in the client
    """
    # Get arguments passed to the url
    if request.args.get('state') != login_session['state']:
        return redirect(url_for('home'))
    else:
        return render_template("profile.html", state=login_session['state'] )


# register template
@app.route('/register', methods=["GET"])
def register():
    """
        :returns the register page
    """
    return render_template("register.html")


# adding asynchronously
@app.route('/register/ajax_post/', methods=["POST"])
def ajaxAdd():
    """
        Adds users asynchronously
    """

    ### NEED TO MODIFY \/\/\/\/\/\/\/ #####
    try:

        data = request.data
        newDict = json.loads(data)
        print(newDict, file=sys.stderr)
        print(data, file=sys.stderr)
        print(session.query(Users).filter_by(username=newDict['username']).count(), file=sys.stderr)
        # check if username is already in use
        assert session.query(Users).filter_by(username=newDict['username']).count() == 0
        print('passed first assertion',file=sys.stderr)
        assert session.query(Users).filter_by(email=newDict['email']).count() == 0
        newUser = Users(username=newDict['username'],
                        password=newDict['password'],
                        email=newDict['email'],
                        name=newDict['name'],
                        telephone=newDict['telephone'])
        newAdress = Adress(adress_line=newDict['address_line'],
                           username=newDict['username'],
                           City=newDict['city'],
                           State=newDict['state'],
                           Zip_Code=newDict['zip_code']
                           )
        session.add(newAdress)
        session.add(newUser)
        session.commit()
        print(str(session.query(Users).all()), file=sys.stderr)
        return data
    except:
        raise Exception("Something went wrong in the server find the bug")
    ### NEED TO MODIFY ^^^^^^^^^^^^^^ ####


# Log out asynchronously
@app.route('/logout', methods=['POST'])
def logout():
    try:
        input_state = request.args.get('state')
        assert input_state == login_session['state']
        login_session['login_bool'] = False
        login_session['current_user'] = None
        return 'done'
    except:
        raise Exception('STATE FAILURE')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



@app.route('/people')
def showUsers():
    users = session.query(Users).all()
    return jsonify(users.JsonReturn)

if __name__ == "__main__":
    app.secret_key = "prototype"
    app.run(debug=True, port=5000, host='0.0.0.0')
