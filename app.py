from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
from SQLfunctions import *
from random import randint

# Initiate Flask app
app = Flask(__name__)
app.secret_key = "abc"

# MYSQL connection setting
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DATABASE'] = 'webshop'
mysql = MySQL(app)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'simon@hotmail.com' and form.password.data == 'password':
            flash('You Are Now Logged In!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid Email Or Password', 'danger')
    return render_template('login.html', form=form)


@app.route('/')
def index():

    # Initiate session-variable
    session['userid'] = randint(0, 10000)

    # Fetch all rows from product-table
    prod = getTable('products', mysql)
    return render_template('index.html', prod = prod)

@app.route('/product')
def product():
    args = request.args
    prod = getRow('products', 'prodID='+args.get("id"), mysql)
    return render_template('productpage.html', prod = prod)

@app.route('/getuser')
def getSess():
    if 'userid' in session:
        res = session['userid']
    return render_template('getuser.html', res = res)

if __name__ == "__main__":
	app.run(debug = True)
