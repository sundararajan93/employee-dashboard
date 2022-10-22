from flask import Flask, render_template, flash, url_for, redirect, session, logging, request
import os
import qrcode
from data import Staff
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
app = Flask(__name__)
from functools import wraps
import time

#
app.config['UPLOAD_FOLDER'] = os.path.join('static','qrcodes')

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ourstaffapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


'''
app.config['MYSQL_HOST'] = '172.17.0.3'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ourstaffapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
'''

# Init MySQL
mysql = MySQL(app)

Staff = Staff()


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


class RegisterForm(Form):
    name = StringField('Name', [validators.required(), validators.Length(min=4, max=50)])
    username = StringField('Username', [validators.required(), validators.Length(min=4, max=50)])
    email = StringField('Email', [validators.DataRequired(),
                                  validators.Length(min=4, max=100)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Passwords do not Match')])
    confirm = PasswordField('confirm')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Creating cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username
                                                                                                   , password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Registered Successfully', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_entered = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_entered, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = "Username or Password is wrong"
                return render_template('login.html', error=error)

            cur.close()

        else:
            error = "Username or Password is wrong"
            return render_template('login.html', error=error)

    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You are not authorized, Please login", 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route('/staff_detail')
@is_logged_in
def staff_detail():
    return render_template("staff_detail.html", staff=Staff)


@app.route('/users')
@is_logged_in
def users():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")

    if result > 0:
        data = cur.fetchall()

    return render_template("users.html", data=data)


@app.route('/qrgen', methods=['GET', 'POST'])
def qrgen():
    if request.method == 'POST':
        detail = request.form['qrdetail']
        qr = qrcode.make(detail)
        folder = os.path.join(app.config['UPLOAD_FOLDER'])
        filename = int(time.time())
        file_path = os.path.join(folder, str(filename) + '.png')
        qr.save(os.path.join(folder, str(filename) + '.png'))
        print("file saved", file_path)
        f = os.path.join(folder, str(filename) + '.png')
        return render_template('qr.html', f=f)

    return render_template("qrgen.html")

@app.route('/qr')
def qr():
    return render_template('qr.html')


@app.route('/staff/<emp_id>/')
@is_logged_in
def staff(emp_id):
    val = int(emp_id)-1
    name = Staff[val]
    return render_template("staff.html", Staff=Staff, emp_id=emp_id, name=name)


if __name__ == '__main__':
    app.secret_key = 'secretkey123'
    app.run(host='0.0.0.0', port=5000, debug=True)
