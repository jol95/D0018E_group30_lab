#-*- coding: -utf-8 -*-
# installed libs
from flask import Flask, render_template, request, session, flash, redirect, url_for

# created libs
from SQLfunctions import *
from forms import *

# Initiate Flask app
app = Flask(__name__)
app.secret_key = "abc"

## REGISTER PAGE ##
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():        
####    
#TODO: SQL insert form data into customer table
####
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('index'))
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
        flash('Please log in or create an account.')
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

    flash('Product has been added to the shopping cart.')
    return redirect('/product?id='+prodID)


#TODO: Skapa en sida som visar alla poster i kundvagnen
@app.route('/cart')
def cart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.')
        return redirect('/login')
    cart = getTable('cart')
    return render_template('cart.html', cart = cart)


# länk för att cleara session
@app.route('/ds')
def dropsess():
    session.clear()
    return redirect('/')

# länk för att starta session
@app.route('/startsess')
def startsess():
    session['userid'] = 1891
    return redirect('/')

if __name__ == "__main__":
	app.run(debug = True)
