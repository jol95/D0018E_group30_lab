#-*- coding: -utf-8 -*-
# installed libs
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_mysqldb import MySQL

# created libs
from SQLfunctions import *
from forms import *


app = Flask(__name__)
app.secret_key = "abc"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'

mysql = MySQL(app)

## REGISTER PAGE ##
@app.route("/register", methods=['GET', 'POST'])
def register():  
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO customers (firstname,lastname,email, password, address, postcode, country, phoneno) VALUE(%s,%s,%s,%s,%s,%s,%s, %s)', (form.first_name.data,form.last_name.data,form.email.data,form.password.data,form.home_address.data,form.post_code.data,form.country.data,form.phone_number.data ))
        mysql.connection.commit()
        #flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('/'))
    return render_template('register.html', form=form)


## LOGIN PAGE ##
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


## INDEX PAGE ##
@app.route('/')
def index():
    # Fetch all rows from product-table
    prod = getTable('products')
    return render_template('index.html', prod = prod)


## PRODUCT PAGE ##
@app.route('/product')
def product():
    args = request.args
    item = getRow('products', 'prodID='+args.get("id"))
    return render_template('productpage.html', item = item)


## ADD TO CART FUNCTION ##
@app.route('/addtocart')
def addtocart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    
    # attribute data for shoping cart
    custID = str(session['userid'])  # temporary customer ID (unregistred user)
    prodID = str(request.args.get('id')) # productID
    qty = str(request.args.get('qty'))   # quantity
    cond = 'custID = '+custID+' AND prodID = '+prodID   # insert/update condition
    
    # check if the product already exists in users cart
    if exist('cart', cond):
        inCart = getRow('cart', cond)
        # increase the quantity of existing product
        addqty = str(int(inCart[3])+int(qty))
        updateIn('cart', 'qty', addqty, cond)
    else:
        # add new product to the cart
        attr = 'custID, prodID, qty'
        values = '%s, %s, %s' %(custID, prodID, qty)
        insertTo('cart', attr, values)

    flash('Product has been added to the shopping cart.', 'success')
    return redirect('/product?id='+prodID)

## CART PAGE ##
@app.route('/cart')
def cart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    attr = 'cart.prodID, products.name, cart.qty'
    join = 'products ON cart.prodID = products.prodID'
    cond = 'cart.custID ='+str(session['userid'])
    cart = innerJoin('cart', attr, join, cond)
    lenofcart = len(cart)
    return render_template('cart.html', cart = cart, lenofcart=lenofcart)

## UPDATE CART FUNCTION ##
@app.route('/updatecart')
def updatecart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')

    custID = str(session['userid'])  # temporary customer ID (unregistred user)
    prodID = str(request.args.get('id')) # productID
    qty = str(request.args.get('qty'))   # quantity
    cond = 'custID = '+custID+' AND prodID = '+prodID   # insert/update condition
    updateIn('cart', 'qty', qty, cond)
    flash('The cart has been updated.', 'success')
    return redirect('/cart')

## CLEAR CART FUNCTION ##
@app.route('/clearcart')
def clearcart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    deleteFrom('cart', 'custID='+str(session['userid']))
    return redirect('/cart')

@app.route('/confirmclear')
def confirmclear():
    return redirect('/cart?confirm=True')


# länk för att cleara session
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# länk för att starta session
@app.route('/startsess')
def startsess():
    session['userid'] = 1891
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
