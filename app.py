# installed libs
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_mysqldb import MySQL
from random import randint

# created libs
from SQLfunctions import *
from forms import *

# Initiate Flask app
app = Flask(__name__)
app.secret_key = "abc"

# MYSQL connection setting
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'
mysql = MySQL(app)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():        
####    
        

####
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'simon@hotmail.com' and form.password.data == 'password':
            flash('You Are Now Logged In!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid Email Or Password', 'danger')
    return render_template('login.html', form=form)


@app.route('/')
def index():
    # Fetch all rows from product-table
    prod = getTable('products', mysql)
    return render_template('index.html', prod = prod)

@app.route('/product')
def product():
    args = request.args
    prod = getRow('products', 'prodID='+args.get("id"), mysql)
    return render_template('productpage.html', prod = prod)

@app.route('/addtocart')
def cart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.')
        return redirect('/login')
    
    # attribute data for shoping cart
    custID = str(session['userid'])  # temporary customer ID (unregistred user)
    prodID = str(request.args.get('id')) # productID
    qty = str(request.args.get('qty'))   # quantity

    #TODO: Lägg till i en shopping cart fungerar. Lägg till till en existerande shopping cart fungerar inte.
    # Add to shopping cart
    insertTo('cart', 'custID, prodID, qty', custID+', '+prodID+', '+qty, mysql)

    flash('Product has been added to the shopping cart.')
    return redirect('/product?id='+prodID)


# länk för att cleara session
@app.route('/ds')
def dropsess():
    session.clear()
    return redirect('/')

# länk för att starta session
@app.route('/startsess')
def startsess():
    session['userid'] = 1981
    return redirect('/')

if __name__ == "__main__":
	app.run(debug = True)
