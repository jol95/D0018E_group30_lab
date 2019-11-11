from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'chonratidpangdee'

app.config['MYSQL_HOST'] = '40.114.198.145:3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = 'Something went wrong blame Chonratid Pangdee'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Customers WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        Customers = cursor.fetchone()
        # If account exists in accounts table in out database
        if webshop:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = webshop['id']
            session['email'] = webshop['email']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or email/password incorrect
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = 'This Chonratid Pangdee guy...'
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form\
            and 'firstname' in request.form and 'lastname' in request.form\
            and 'phonenr' in request.form and 'address' in request.form\
            and 'postcode' in request.form and 'city' in request.form\
            and 'country' in request.form and 'dob' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenr = request.form['phonenr']
        address = request.form['address']
        postcode = request.form['postcode']
        city = request.form['city']
        country = request.form['country']
        dob = request.form['dob']

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

if __name__ == '__main__':
    app.run()


#130.240.200.55:80