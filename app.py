import string

from math import log2
from random import sample, randint
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, send_file
from flask_session import Session
from flask_mail import Mail, Message
from validate_email import validate_email
from werkzeug.security import check_password_hash, generate_password_hash
from cryptography.fernet import Fernet
from helpers import login_required

app = Flask("__name__")
db = SQL("sqlite:///C:/Users/Hyde/Documents/Code/HydPass/accounts.db")

# MAIL CONFIGURATIONS
app.config['MAIL_DEFAULT_SENDER'] = 'bot.hydpass@gmail.com'
app.config["MAIL_USERNAME"] = "bot.hydpass@gmail.com"
app.config["MAIL_PASSWORD"] = "hnihmlvsxezfwcse"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
mail = Mail(app)

# SESSION CONFIGURATIONS
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_NAME"] = "session"
Session(app)

# WARNING TEXTS
emptyField = "One or more input fields are empty!"
invalidEmail = "Invalid Email!"
notRegistered = "Email not yet registered!"
differentPw = "Passwords are not the same!"
inputWrong = "One or more input fields are wrong!"
emailTaken = "Email is already taken!"

# Global Variables HTML
fernet = Fernet(b'X69w4JsqC_XF19FeeZDCuwQZDB3tDZQ97ZEq0tJhEC8=')
app.jinja_env.globals.update(session=session)
app.jinja_env.globals.update(fernet=fernet)
app.jinja_env.globals.update(enumerate=enumerate)

# Global Variables PYTHON
possibleUser = None
possibleMail = None
possiblePass = None

@app.route("/", methods=["GET", "POST"])
def home():
    # If the user is logged in display username
    if request.method == "GET":
        if session.get("loggedUser"):
            return render_template("home.html", logged=True)

        return render_template("home.html")

    loggedMail = session["loggedMail"][0]["email"]
    password = request.form.get("password")
    confirmPassword = db.execute("SELECT password FROM users WHERE email = ?", loggedMail)

    if (check_password_hash(confirmPassword[0]["password"], password)):
        return jsonify(True)

    return jsonify(False)

# REGISTER LOGOUTS AND THE LIKE ----------------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    session.clear()
    session["CURRENT_ACTION"] = "register"

    # Get given inputs
    username = request.form.get("username").strip()
    email = request.form.get("email").strip().lower()
    password = request.form.get("password")
    passwordVerify = request.form.get("passwordVerify")

    # Fail cases
    if not username or not email or not password or not passwordVerify:
        return render_template("register.html", warning=True, warningText=emptyField)

    if validate_email(email) == False:
        return render_template("register.html", warning=True, warningText=invalidEmail)

    if password != passwordVerify:
        return render_template("register.html", warning=True, warningText=differentPw)

    if len(db.execute("SELECT email FROM users WHERE email = ?", email.lower())) >= 1:
        return render_template("register.html", warning=True, warningText=emailTaken)

    # Set values to session to access in other functions
    session["otp"] = randint(100000, 999999)

    # Send email with one time pass to the given user email
    message = Message(f"Thank you for registering to HydPass, {username}!", recipients=[email])
    message.body = f"Here is your OTP: {session.get('otp')}"
    mail.send(message)

    session["username"] = username
    session["email"] = email
    session["password"] = generate_password_hash(password, method="pbkdf2:sha256:260000", salt_length=25)

    return render_template("register.html", success=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    session.clear()
    session["CURRENT_ACTION"] = "login"

    # Get given email and password
    email = request.form.get("email").strip().lower()
    password = request.form.get("password")

    # If fields are blank return error
    if not email or not password:
        return render_template("login.html", warning=True, warningText=emptyField)

    # If email isn't real return error
    if validate_email(email) == False:
        return render_template("login.html", warning=True, warningText=invalidEmail)

    # Get the password for the email account
    passwordAcc = db.execute("SELECT password FROM users WHERE email = ?", email.lower())

    # If account doesn't exist return error
    if not passwordAcc:
        return render_template("login.html", warning=True, warningText=notRegistered)

    # Check if passwords are the same
    if not check_password_hash(passwordAcc[0]["password"], password):
        return render_template("login.html", warning=True, warningText=inputWrong)

    # Generate OTP and send it to the given user
    session["otp"] = randint(100000, 999999)

    global possibleUser
    global possibleMail

    possibleUser = db.execute("SELECT username FROM users WHERE email = ?", email)
    possibleMail = db.execute("SELECT email FROM users WHERE email = ?", email)

    message = Message("OTP for HydPass login!", recipients=[email])
    message.body = f"Here is your OTP: {session.get('otp')}"
    mail.send(message)

    return render_template("login.html", success=True)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "GET":
        return render_template("logout.html")

    session.clear()
    return redirect("/login")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    # Get the session and the given OTP
    otp = session["otp"]
    userOTP = request.form.get("otp")

    # If there is no session OTP return to homepage
    if request.method == "GET" or not otp:
        return redirect("/")

    # If the given otps are not real then return error
    if userOTP != str(otp):
        return render_template("verify.html")

    # Reset otp and check if registering or logging in
    session["otp"] = None
    CURRENT_ACTION = session["CURRENT_ACTION"]

    global possibleUser
    global possibleMail
    global possiblePass

    # If registering add user to the database, if logging in set cookie to username
    if CURRENT_ACTION == "register":
        db.execute("INSERT INTO users (username, email, password) VALUES(?, ?, ?)" , session.get("username"), session.get("email"), session.get("password"))
    elif CURRENT_ACTION == "login":
        session["loggedUser"] = possibleUser
        session["loggedMail"] = possibleMail
        possibleUser = None
        possibleMail = None
    elif CURRENT_ACTION == "editEmail":
        email = session["loggedMail"][0]["email"]
        db.execute("UPDATE users SET email = ? WHERE email = ?", possibleMail, email)
        db.execute("UPDATE users SET loggedUser = ? WHERE email = ?", possibleMail, email)
        session["loggedMail"] = db.execute("SELECT email FROM users WHERE email = ?", possibleMail)

        possibleMail = None
    elif CURRENT_ACTION == "editPass":
        email = session["loggedMail"][0]["email"]
        print(possiblePass)
        password = generate_password_hash(possiblePass, method="pbkdf2:sha256:260000", salt_length=25)
        db.execute("UPDATE users SET password = ? WHERE email = ?", password, email)
        session.clear()

    # Reset current action and return success
    session["CURRENT_ACTION"] = None
    return render_template("verify.html", success=True, success2=True)

@app.route("/edit-account", methods=["GET", "POST"])
@login_required
def editAccount():
    if request.method == "GET":
        return render_template("edit_account.html")

    userEmail = session["loggedMail"][0]["email"]
    userPass = db.execute("SELECT password FROM users WHERE email = ?", userEmail)[0]["password"]

    action = request.form.get("action")
    password = request.form.get("password")

    if action == "editEmail":
        if not check_password_hash(userPass, password):
            return jsonify("wrongPass")

        email = request.form.get("email").strip().lower()

        if not validate_email(email):
            return jsonify("invalidEmail")

        if len(db.execute("SELECT email FROM users WHERE email = ?", email)) > 0:
            return jsonify("inUse")

        session["CURRENT_ACTION"] = "editEmail"
        session["otp"] = randint(100000, 999999)

        global possibleMail
        possibleMail = email

        message = Message("OTP for HydPass Email Edit!", recipients=[email])
        message.body = f"Here is your OTP: {session.get('otp')}"
        mail.send(message)

        return render_template("verify.html", success2=True)
    elif action == "editUsername":
        if not check_password_hash(userPass, password):
            return jsonify("wrongPass")
        username = request.form.get("username")
        db.execute("UPDATE users SET username = ? WHERE email = ?", username, userEmail)
        session["loggedUser"] = db.execute("SELECT username FROM users WHERE email = ?", userEmail)
        return jsonify(True)
    elif action == "editPassword":
        global possiblePass
        print(request.form.get("password"))
        possiblePass = request.form.get("password")

        session["CURRENT_ACTION"] = "editPass"
        session["otp"] = randint(100000, 999999)

        message = Message("OTP for HydPass Password Edit!", recipients=[userEmail])
        message.body = f"Here is your OTP: {session.get('otp')}"
        mail.send(message)

    return render_template("verify.html", success2=True)


# SERVICES ----------------------------------------------------------------------------------

@app.route("/generation", methods=["GET", "POST"])
def generate():
    if request.method == "GET":
        # Default if cookies don't exist
        try:
            length    = session["PW_LENGTH"]
            uppercase = session["UPPERCASE"]
            lowercase = session["LOWERCASE"]
            numbers   = session["NUMBERS"]
            symbols   = session["SYMBOLS"]
        except KeyError:
            length = 18
            uppercase = "checked"
            lowercase = "checked"
            numbers   = "checked"
            symbols   = "checked"

        return render_template("generation.html", length=length, uppercase=uppercase, lowercase=lowercase, numbers=numbers, symbols=symbols)

    # Get form submissions
    passLength = request.form.get("passLength")
    inUppercase = request.form.get("uppercase")
    inLowercase = request.form.get("lowercase")
    inNumbers = request.form.get("numbers")
    inSymbols = request.form.get("symbols")

    usedSymbols = []

    # Get value of checkboxes and set cookies
    session["UPPERCASE"] = None
    session["LOWERCASE"] = None
    session["NUMBERS"] = None
    session["SYMBOLS"] = None

    if inUppercase:
        usedSymbols += list(string.ascii_uppercase)
        session["UPPERCASE"] = "checked"

    if inLowercase:
        usedSymbols += list(string.ascii_lowercase)
        session["LOWERCASE"] = "checked"

    if inNumbers:
        usedSymbols += list(string.digits)
        session["NUMBERS"] = "checked"

    if inSymbols:
        usedSymbols += list(string.punctuation)
        session["SYMBOLS"] = "checked"

    # If the given passlength is a valid integer use it, else default to 15 and if its more than the sample just make it the sample size
    try:
        passLength = int(passLength)
    except ValueError:
        passLength = 18

    if passLength > len(usedSymbols):
        passLength = len(usedSymbols)

    session["PW_LENGTH"] = passLength

    # Randomly generate passwords based on given list
    generatedPass1 = (sample(usedSymbols, passLength))
    generatedPass1 = ''.join(generatedPass1)

    # Set cookies
    length = session["PW_LENGTH"]
    uppercase = session["UPPERCASE"]
    lowercase = session["LOWERCASE"]
    numbers = session["NUMBERS"]
    symbols = session["SYMBOLS"]

    return render_template("generation.html", success=True, length=length, uppercase=uppercase, lowercase=lowercase, numbers=numbers, symbols=symbols, password1=generatedPass1)


@app.route("/strength", methods=["GET", "POST"])
def strengthTest():
    # Log2(password character set total) * Length of password
    if request.method == "GET":
        return render_template("strength.html")

    # Get the password input
    password = request.form.get("password")
    orgPass = password

    # Default values
    uppercase = False
    lowercase = False
    symbols = False
    numbers = False

    # Set to use
    usedSymbols = []

    if not password:
        return redirect("/strength")

    # For every character check if its lowercase
    for char in password:
        if char in string.ascii_uppercase and not uppercase:
            uppercase = True
            usedSymbols += string.ascii_uppercase
            continue

        if char in string.ascii_lowercase and not lowercase:
            lowercase = True
            usedSymbols += string.ascii_lowercase
            continue

        if char in string.digits and not numbers:
            numbers = True
            usedSymbols += string.digits
            continue

        if char in string.punctuation and not symbols:
            symbols = True
            usedSymbols += string.punctuation
            continue

    boe = log2(len(usedSymbols)) * len(orgPass)

    if boe < 25:
        passwordFeedback1 = "Your password is very weak and can easily be cracked in a few milliseconds."
    elif boe >= 25 and boe < 50:
        passwordFeedback1 = "Your password is poor and can easily be cracked in less than a second."
    elif boe >= 50 and boe < 75:
        passwordFeedback1 = "Your password is average and can be cracked in a few minutes."
    elif boe >= 75 and boe < 100:
        passwordFeedback1 = "Your password is good and can be cracked in a few hours."
    else:
        passwordFeedback1 = "Your password is very good and cannot be cracked without a massive amount of effort."

    passwordFeedback2 = ""

    if len(orgPass) < 10:
        passwordFeedback2 = "Consider making your password longer."

    if not uppercase or not symbols or not lowercase or not numbers and boe < 100:
        passwordFeedback2 += " Consider adding more variety of different characters, like symbols or lowercase."

    boe = "{:.2f}".format(boe)

    return render_template("strength.html", success=True, uppercase=uppercase, lowercase=lowercase, numbers=numbers, symbols=symbols, boe=boe, passwordFeedback1=passwordFeedback1, passwordFeedback2=passwordFeedback2)


@app.route("/manager", methods=["GET", "POST"])
@login_required
def manager():
    # Get logged user
    loggedMail = session["loggedMail"][0]["email"]

    # If its request method get return all accounts with the logged user
    if request.method == "GET":
        accounts = db.execute("SELECT * FROM manager WHERE loggedUser = ?", loggedMail)
        return render_template("manager.html", accounts=accounts)

    # If not then they are trying to delete the account, so verify the password and if its not the same as the logged in account return false
    password = db.execute("SELECT password FROM users WHERE email = ?", loggedMail)
    password = password[0]["password"]
    passwordConfirm = request.form.get("passwordConfirm")

    if not check_password_hash(password, passwordConfirm):
        return jsonify(False)

    action = request.form.get("action")

    if action == "delete":
        # If it returns true get the data
        website = request.form.get("website")
        email = request.form.get("email")
        username = request.form.get("username")
        passwordForm = request.form.get("password")

        # get the accounts with the same data, except password
        validPasswords = db.execute("SELECT * FROM manager WHERE loggedUser = ? AND username = ? AND email = ? AND website = ?", loggedMail.lower(), username, email, website)

        # Decode the password and check if its the same, and if it is delete it and return true
        for password in validPasswords:
            if fernet.decrypt(password["password"]).decode() == passwordForm:
                db.execute("DELETE FROM manager WHERE loggedUser = ? AND id = ?", loggedMail, password["id"])
                break
    elif action == "edit":
        website = request.form.get("orgWebsite")
        email = request.form.get("orgEmail").lower()
        username = request.form.get("orgUsername")
        password = request.form.get("orgPassword")

        newWebsite = request.form.get("editWebsite")
        newEmail = request.form.get("editEmail")
        newUsername = request.form.get("editUsername")
        newPassword = request.form.get("editPassword")
        newPassword = fernet.encrypt(newPassword.encode())

        if not newEmail.strip():
            newWebsite = "-"

        if not newUsername.strip():
            newUsername = "-"

        validSelections = db.execute("SELECT * FROM manager WHERE loggedUser = ? AND username = ? AND email = ? AND website = ?", loggedMail.lower(), username, email, website)

        for selection in validSelections:
            if fernet.decrypt(selection["password"]).decode() == password:
                db.execute("UPDATE manager SET website = ?, email = ?, password = ?, username = ? WHERE loggedUser = ? AND id = ?", newWebsite, newEmail, newPassword, newUsername, loggedMail, selection["id"])
                break

    return jsonify(True)

# MANAGER FUNCTIONS -----------------------------------------------------------------------------

@app.route("/add-account", methods=["GET", "POST"])
@login_required
def add_account():
    # If request get render the form
    if request.method == "GET":
        return render_template("add_account.html")

    # Get the logged user and get the form
    loggedUser = session["loggedMail"][0]["email"]

    website = request.form.get("website")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # If they left website or password empty, return
    if not website or not password:
        return render_template("add_account.html", warning=True, warningText=emptyField)

    # If username or email is blank replace it with "-"
    if not username.strip():
        username = "-"

    if not email.strip():
        email = "-"

    # Encrypt entered password
    password = fernet.encrypt(password.encode())

    # Insert info
    db.execute("INSERT INTO manager (loggedUser, username, email, password, website) VALUES (?, ?, ?, ?, ?)", loggedUser, username, email, password, website)
    return redirect("/manager")


# EXTERNAL JAVASCRIPTS --------------------------------------------

@app.route('/static/<path:filename>')
def send_js(filename):
    return send_file(app.static_folder, filename, mimetype='text/javascript')