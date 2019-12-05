#-*- coding: -utf-8 -*-
# installed libs
from flask import *
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image
from werkzeug.utils import secure_filename

# created libs
from SQLfunctions import *
from forms import *

# Initiate Flask app
app = Flask(__name__)
app.secret_key = "abc"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'

app.config['UPLOAD_FOLDER'] = '/var/www/html/static/resources'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["JPG", "PNG"]



mysql = MySQL(app)

#TODO: Kontroll om användaren redan finns i databasen.
## REGISTER PAGE ##
@app.route("/register", methods=['GET', 'POST'])
def register():  
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        email = form.email.data
        cur.execute('SELECT * FROM customers WHERE email = %s', [email])
        data = cur.fetchall()

        if len(data) > 0:
            flash('Email Already exist!', 'danger')

        else:
            cur = mysql.connection.cursor()
            profile_pic = 'default.jpg'
            hashed_password = generate_password_hash(form.password.data)
            cur.execute(
                'INSERT INTO customers (firstname,lastname,email, password, address, postcode, country, phoneno, profilepic)'
                ' VALUE(%s,%s,%s,%s,%s,%s,%s, %s, %s)', (form.first_name.data, form.last_name.data, form.email.data,
                                                         hashed_password, form.home_address.data, form.post_code.data,
                                                         form.country.data, form.phone_number.data, profile_pic))
            mysql.connection.commit()
            flash('You Have Created An Account!', 'success')
            return redirect('/')
    return render_template('register.html', form=form)


## LOGIN PAGE ##
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        email = form.email.data
        cur.execute('SELECT * FROM customers WHERE email = %s', [email])
        data = cur.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][4]), form.password.data):
                session['userid'] = data[0][0]
                session['username'] = data[0][1]
                flash('You Are Now Logged In!', 'success')
                return redirect('/')
            else:
                flash('Invalid Email Or Password', 'danger')
        else:
            flash('Invalid Email Or Password', 'danger')
    return render_template('login.html', form=form)



## INDEX PAGE ##
@app.route('/')
def index():
    # Fetch all rows from product-table
    prod = getTable('products')
    print prod
    return render_template('index.html', prod = prod)


## PRODUCT PAGE ##
@app.route('/product', methods=['GET', 'POST'])
def product():
    form = ReviewForm()
    args = request.args
    item = getRow('products', 'prodID='+args.get("id"))
    rev = getTable('reviews WHERE prodID=%s'%(item[0]))
    ## SUBMITTING REVIEWS ##
    if request.method=='POST':
        prodID = item[0]
        custID = str(session['userid'])
        text = form.text.data
        date = '12'
        attr = 'prodID, custID, text, date'
        val = '%s, %s, "%s", %s' %(prodID, custID, text, date)
        insertTo('reviews', attr, val)
        flash('Thank you for leaving a review!', 'success')
        return redirect('/product?id=%s' %item[0])
    return render_template('productpage.html', item = item, form=form, rev=rev)


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
        updateAll('cart', 'qty='+addqty, cond)
    else:
        # add new product to the cart
        attr = 'custID, prodID, qty'
        values = '%s, %s, %s' %(custID, prodID, qty)
        insertTo('cart', attr, values)

    flash('Product has been added to the shopping cart.', 'success')
    return redirect('/product?id='+prodID)


#TODO: Bekräfta order funktion
## CART PAGE ##
@app.route('/cart')
def cart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    attr = 'cart.prodID, products.name, cart.qty'
    join = 'products ON cart.prodID = products.prodID'
    cond = 'cart.custID = '+str(session['userid'])
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

# länk för att starta admin session
@app.route('/startadmin')
def startsess():
    session['userid'] = 1891
    session['username'] = 'admin'
    return redirect('/')


## ADMIN - CUSTOMER PAGES ##
@app.route('/admin/customers', methods=['GET', 'POST'])
def admin_customers():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')

    # define page
    page = ''

    # intiate seach form
    custSearch = adminProdSearch()  # same form as ProdSearc
    res = ''  # empty search result

    # seach by customer number, name or e-mail
    if request.method == 'POST':
        searchWord = str(custSearch.search.data)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM customers WHERE firstname LIKE "%' + searchWord + \
                    '%" OR lastname LIKE "%' + searchWord + '%" OR custID LIKE "%' + searchWord + '%" OR email LIKE "%' + searchWord + '%"')
        res = cur.fetchall()
        cur.close()

        # flash message if customer not found
        if len(res):
            page = 'searchresult'
        else:
            flash('Customer not found.', 'danger')

    # show all customers
    if request.args.get('page') == 'showall':
        res = getTable('customers')
        page = 'searchresult'

    return render_template('admin/customers.html', form=custSearch, res=res, p=page)


## ADMIN - EDIT CUSTOMERS ##
@app.route('/admin/customer/edit', methods=['GET', 'POST'])
def admin_customers_edit():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')

    # define page
    page = 'customer edit'

    # initialize edit form (same as RegistrationForm)
    editCust = RegistrationForm()

    # get customer info
    custInfo = getRow('customers', 'custID=%s' %(request.args.get('custid')))

    # update the customer info
    if request.method == 'POST':
        fname = str(editCust.first_name.data)
        lname = str(editCust.last_name.data)
        email = str(editCust.email.data)
        addr = str(editCust.home_address.data)
        pcode = str(editCust.post_code.data)
        country = str(editCust.country.data)
        phone = str(editCust.phone_number.data)
        update = 'a.firstname="%s", a.lastname="%s", a.email="%s", a.address="%s", a.postcode="%s", \
            a.country="%s", a.phoneno="%s"' %(fname, lname, email, addr, pcode, country, phone)
        # cond = 'custID = %s' %(str(request.form.get('custID')))
        cond = 'custID = %s' %(str(request.args.get('custid')))
        updateAll('customers as a', update, cond)
        flash('Update sucessfull!', 'success')
        return redirect('/admin/customer/edit?custid='+str(custInfo[0]))

    return render_template('admin/customers.html', form=editCust, cust=custInfo, p=page)

## ADMIN - PRODUCT PAGES ##
@app.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')

    # define page
    page = 'products'

    # initialize searchbar
    form = adminProdSearch()

    # search by item number or product name
    if request.method=='POST':
        searchWord = str(form.search.data)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM products WHERE name LIKE "%'+searchWord+'%" OR prodID LIKE "%'+searchWord+'%"')
        res = cur.fetchall()
        cur.close()
    else:
        res = getTable('products')      # default "show all products"

    # error message on search
    if len(res) == 0:
        flash('Your search "'+form.search.data+'" did not match any product(s).', 'warning')

    return render_template('admin/products.html', form=form, prod=res, p=page)

@app.route('/admin/product/edit', methods=['GET', 'POST'])
def admin_products_edit():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    # define page
    page = 'Edit'

    # initalize edit form
    editform = adminProdEdit()

    # update the product
    if request.method == 'POST':
        update = 'name="%s", desc="%s", price=%s, img="%s", stock=%s, category=%s, discount=%s' %(editform.name.data, editform.desc.data, editform.price.data, editform.img.data, editform.stock.data, editform.cat.data, editform.discount.data)
        cond = 'prodID = %s' %(request.args.get('prodID'))
        return updateAll('products', update, cond)
    # default show the product
    else:
        res = getRow('products', 'prodID ='+request.args.get('id'))

    return render_template('admin/products.html', p=page, form=editform, item=res)
    


## ADMIN - ORDER PAGES ##
@app.route('/admin/orders')
def admin_orders():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')

    return render_template('admin/orders.html')



def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def upload_file(pic_filename):
    #hex_rand = secrets.token_hex(8)
    #picture_fn = secure_filename(pic_filename.filename)
    #_, f_ext = os.path.splittext(pic_filename.filename)
    #picture_fn =  + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_filename)

    standard_size = (125, 125)
    pic = Image.open(pic_filename)
    pic.thumbnail(standard_size)
    pic.save(picture_path)
    return picture_fn



@app.route("/customerMypage", methods=['GET', 'POST'])
def customerMypage():
    form = customerMypageform()
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    custID = str(session['userid'])
    cur.execute('SELECT * FROM customers WHERE custID = %s', [custID])
    data = cur.fetchone()
    profile_pic = data[9]

    if form.validate_on_submit():
        if form.picture.data:
            image = form.picture.data
            if allowed_image(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_pic = filename
                print SPARAT BILD
                print filename
            else:
                flash('File Extention Is Not Allowed', 'success')


        fname = str(form.first_name.data)
        lname = str(form.last_name.data)
        email = str(form.email.data)
        addr = str(form.home_address.data)
        pcode = str(form.post_code.data)
        country = str(form.country.data)
        phone = str(form.phone_number.data)
        update = 'a.firstname="%s", a.lastname="%s", a.email="%s", a.address="%s", a.postcode="%s", \
                   a.country="%s", a.phoneno="%s", a.profilepic="%s"' % (fname, lname, email, addr, pcode, country, phone, profile_pic)

        cond = 'custID = %s' % (str(request.args.get('custid')))
        print SKA LAGGA IN I DATABAS
        updateAll('customers as a', update, cond)

        flash('Your Account Info Has Been Updated!', 'success')
        #return redirect(url_for('customerMypage'))

    image_file = url_for('static', filename='resources/' + profile_pic)

    return render_template('customerMypage.html', image_file=image_file, form=form, data=data)

if __name__ == "__main__":
	app.run(debug = True)


# TEST TEST TEST
