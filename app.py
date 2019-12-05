#-*- coding: -utf-8 -*-
# installed libs
from flask import *
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# created libs
from forms import *
from SQLfunctions import *
import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'bdb878ef8ea259ef877a3686726cf4f9'

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
        profile_pic = 'default.jpg'
        hashed_password = generate_password_hash(form.password.data)
        cur.execute('INSERT INTO customers (firstname,lastname,email, password, address, postcode, country, phoneno, profilepic)'
                    ' VALUE(%s,%s,%s,%s,%s,%s,%s, %s, %s)',(form.first_name.data, form.last_name.data, form.email.data,
                                                        hashed_password, form.home_address.data,form.post_code.data,
                                                        form.country.data, form.phone_number.data, profile_pic))
        mysql.connection.commit()
        flash('You Have Created An Account!', 'success')
        return redirect('/')
    return render_template('register.html', form=form)


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

@app.route("/customerMypage")
def customerMypage():

    return render_template('customerMypage.html')

## INDEX PAGE ##
@app.route('/', methods=['GET', 'POST'])
def index():
    # show search result
    if request.method=='POST' and len(request.form.get('searchword')) :
        res = getTable('products WHERE name LIKE "%'+request.form.get('searchword')+
        '%" OR prodID LIKE "%'+request.form.get('searchword')+'%"')
    else:
        # Fetch all rows from product-table
        res = getTable('products')
    return render_template('index.html', prod = res)


## PRODUCT PAGE ##
@app.route('/product', methods=['GET', 'POST'])
def product():
    form = ReviewForm()
    args = request.args
    item = getRow('products', 'prodID='+args.get("id"))
    ## GET REVIEWS ##
    attr = 'customers.firstname, reviews.date, reviews.text, reviews.stars'
    join = 'customers ON reviews.custID = customers.custID'
    cond = 'reviews.prodID=%s' %(item[0])
    rev = innerJoin('reviews', attr, join, cond)

    ## SUBMITTING REVIEWS ##
    if request.method=='POST' and request.args.get('action') == 'addreview':
        prodID = item[0]
        custID = str(session['userid'])
        text = form.text.data
        attr = 'prodID, custID, text'
        val = '%s, %s, "%s"' %(prodID, custID, text)
        insertTo('reviews', attr, val)
        flash('Thank you for leaving a review!', 'success')
        return redirect('/product?id=%s' %item[0])
    return render_template('productpage.html', item = item, form=form, rev=rev)

## ADD TO CART FUNCTION ##
@app.route('/addtocart', methods=['GET', 'POST'])
def addtocart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    
    # attribute data for shoping cart
    custID = str(session['userid'])  # temporary customer ID (unregistred user)
    prodID = str(request.args.get('id')) # productID
    qty = str(request.form.get('qty')) if request.form.get('qty') else str(request.args.get('qty'))   # quantity
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
    return redirect(url_for('cart'))

## CART PAGE ##
@app.route('/cart')
def cart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')

    # getting cart
    attr = 'cart.prodID, products.name, products.price, cart.qty'
    join = 'products ON cart.prodID = products.prodID'
    cond = 'cart.custID ='+str(session['userid'])
    cart = innerJoin('cart', attr, join, cond)
    lenofcart = len(cart)

    # calculate the total amount of the cart
    totalamount = 0
    for items in cart:
        totalamount += int(items[2])*int(items[3])
    
    return render_template('cart.html', cart = cart, lenofcart=lenofcart,\
        totalamount=totalamount)

## UPDATE CART FUNCTION ##
@app.route('/updatecart', methods=['GET', 'POST'])
def updatecart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')

    # update post in the cart
    if request.args.get('action') == 'update':
        cond = 'custID=%s and prodID=%s' %(str(session['userid']),\
            request.form.get('id'))
        if int(request.form.get('qty')) == 0:
            deleteFrom('cart', cond)
            flash('Item %s has been removed from the cart.' \
                %(str(request.form.get('id'))), 'danger')
        else:
            updateIn('cart', 'qty', str(request.form.get('qty')),cond)
            flash('The cart has been updated.', 'success')
    
    # delete post in the cart
    if request.args.get('action') == 'delete':
        cond = 'custID=%s and prodID=%s' %(str(session['userid']),\
            str(request.args.get('id')))
        deleteFrom('cart', cond)
        flash('Item %s has been removed from the cart.' %(str(request.args.get('id'))), 'danger')

    # clear cart
    if request.args.get('action') == 'clear':
        deleteFrom('cart', 'custID='+str(session['userid']))
        flash('Your cart has been cleared.', 'danger')

    return redirect('/cart')

## CHECKOUT PAGE ##
@app.route('/checkout')
def checkout():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')

    # get shopping cart
    attr = 'cart.prodID, products.name, products.price, products.discount, cart.qty'
    join = 'products ON cart.prodID = products.prodID'
    cond = 'cart.custID ='+str(session['userid'])
    cart = innerJoin('cart', attr, join, cond)

    if len(cart) <= 0:
        flash('Nothing to checkout.', 'danger')
        return redirect(url_for('cart'))
    else:
        # create order
        insertTo('orders', 'custID, status, amount', '{}, 0, 0'.format(session['userid']))
        orderno = getOne('orders', 'orderID',
        'custID={} ORDER BY orderID DESC'.format(session['userid']))

        # move cart to orderlines
        lineno = 1  # initiate linenumber for each order
        cartamount = 0 # order amount
        for post in cart:
            insertTo('orderln', 'orderID, lineno, prodID, qty, price, discount',
            '{}, {}, {}, {}, {}, {}'.format(orderno[0], lineno, post[0],
            str(post[4]), str(post[2]), str(post[3])))
            lineno+=1   # increase line number
            cartamount += post[2]*(100-post[3])/100*post[4] # total amount
        
        # insert cart amount to order amount
        updateAll('orders', 'amount={}'.format(str(cartamount)), 'orderID={}'.format(orderno[0]))
        
        # delete cart once moved to order
        deleteFrom('cart', 'custID='+str(session['userid']))
        
        # flash message to customer
        flash('Thank you for placing your order!', 'success')

    return redirect(url_for('index'))

## ORDER PAGE ##
@app.route('/orders')
def orders():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    
    # getting customers orders information
    attr = 'o.orderID, o.date, o.amount, t.text'
    join = 'text as t ON o.status = t.textid'
    cond = 'o.custID={} AND t.typeid=2 ORDER BY o.orderID ASC'.format(session['userid'])
    orders = innerJoin('orders as o', attr, join, cond)
    orderrows = ''
    totalamount = getSum(table='orders', column='amount',
    condition='custID={}'.format(session['userid']))
    # return str(totalamount('decimal'))

    # getting order rows
    if request.args.get('order'):
        orderrows = getTable('orderln WHERE orderID={}'.format(request.args.get('order')))

    return render_template('orders.html', orders=orders, rows=orderrows,
    totalamount=totalamount)

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
    custSearch = adminProdSearch() # same form as ProdSearc
    res = ''    # empty search result

    # seach by customer number, name or e-mail
    if request.method=='POST':
        searchWord = str(custSearch.search.data)
        res = getTable('customers WHERE firstname LIKE "%'+searchWord+\
            '%" OR lastname LIKE "%'+searchWord+'%" OR custID LIKE "%'+searchWord+\
                '%" OR email LIKE "%'+searchWord+'%"')
        
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

    # seach by item number or product name
    if request.method=='POST':
        searchWord = str(form.search.data)
        res = getTable('products WHERE name LIKE "%'+searchWord+
        '%" OR prodID LIKE "%'+searchWord+'%"')
    else:
        res = getTable('products')      # default "show all products"

    # error message on search
    if len(res) == 0:
        flash('Your search "'+form.search.data+'" did not match any product(s).', 'warning')

    return render_template('admin/products.html', form=form, prod=res, p=page)

#ADMIN - EDIT PRODUCT PAGE#
@app.route('/admin/product/edit', methods=['GET', 'POST'])
def admin_products_edit():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    # define page
    page = 'edit'

    prodid = str(request.args.get('id'))

    # initalize edit form
    editform = adminProdEdit()
    # return str(request.args.get('id'))
    res = getRow('products', 'prodID ='+prodid)

    # update the product
    if request.method == 'POST':
        name = str(editform.name.data)
        desc = str(editform.desc.data) if str(editform.desc.data) else str(res[2])
        price = str(editform.price.data)
        stock = str(editform.stock.data)
        cat = str(editform.cat.data)
        disc = str(editform.discount.data)
        update = 'a.name="%s", a.desc="%s", a.price=%s, a.stock=%s, \
            a.category="%s", a.discount=%s' %(name, desc, price, stock, cat, disc)
        cond = 'prodID = %s' %(prodid)
        updateAll('products as a', update, cond)

        # upload picture to static/resources/ and set the prodID as filename
        if editform.img.data:
            prodid = getOne('products', 'prodID',
            'name="{}"'.format(str(editform.name.data)))[0]
            fileextension = editform.img.data.filename[-4:]
            filename = secure_filename(str(prodid)+fileextension)
            editform.img.data.save('static/resources/'+filename)
            updateAll('products', 'img="{}"'.format(filename), 'prodID={}'.format(prodid))

        flash('Update sucessfull!', 'success')
        return redirect(url_for('admin_products')+'?id='+str(request.args.get('id')))
    else:
        editform.desc.data = res[2]
    return render_template('admin/products.html', p=page, form=editform, item=res)

## ADMIN - ADD PRODUCT PAGE ##
@app.route('/admin/product/add', methods=['GET', 'POST'])
def admin_products_add():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    # define page
    page = 'add'

    # initialize add-form (same as edit-form)
    addform = adminProdEdit()

    # add the product
    if request.method == 'POST':
        # form data
        name = str(addform.name.data)
        desc = addform.desc.data
        price = str(addform.price.data) if str(addform.price.data) != "" else '0'
        img = str(addform.img.data.filename) if addform.img.data else 'noimg.jpg'
        stock = str(addform.stock.data) if str(addform.stock.data) != "" else '0'
        cat = str(addform.cat.data) if str(addform.cat.data) != "" else ''

        # product table attributes and values
        attr = '`name`, `price`, `stock`, `img`, `category`, `desc`, `discount`'
        val = '"%s", %s, %s, "%s", %s, "%s", 0' %(name, price, stock, img, cat, desc)
        res = insertTo('products', attr, val)

        # upload picture to static/resources/ and set the prodID as filename
        if addform.img.data:
            prodid = getOne('products', 'prodID',
            'name="{}"'.format(str(addform.name.data)))[0]
            fileextension = addform.img.data.filename[-4:]
            filename = secure_filename(str(prodid)+fileextension)
            addform.img.data.save('static/resources/'+filename)
            updateAll('products', 'img="{}"'.format(filename), 'prodID={}'.format(prodid))

        # flash success to user
        flash('The product has been added!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/products.html', p=page, form=addform)

## ADMIN - DELETE PRODUCT FUNCTION ##
@app.route('/admin/product/delete')
def admin_products_delete():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    # delete the product and flash the user on success
    removeProd = request.args.get('id')
    filename = getOne('products', 'img',
            'prodID={}'.format(removeProd))[0]
    deleteFrom('products', 'prodID='+removeProd)
    os.remove('static/resources/'+filename)
    flash('Item# '+removeProd+' has been successfully removed!', 'success')
    return redirect(url_for('admin_products'))

## ADMIN - ORDER PAGES ##
@app.route('/admin/orders')
def admin_orders():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    return render_template('admin/orders.html')

if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0', port=5000)
