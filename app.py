#-*- coding: -utf-8 -*-
# installed libs
from flask import *
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os, math
from PIL import Image
from werkzeug.utils import secure_filename

from SQLfunctions import *
from forms import *

# Initiate Flask app
app = Flask(__name__)
app.secret_key = "abc"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'

app.config['UPLOAD_FOLDER'] = 'static/resources'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["JPG", "PNG"]


mysql = MySQL(app)

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
@app.route('/', methods=['GET', 'POST'])
def index():
    plimit = 4  # page limit (number of products)
    poffset = int(request.args.get('offset')) if request.args.get('offset') else 0
    categories = fetchall('SELECT textid, text FROM text WHERE typeid=1') # get all categories
    cat = request.args.get('cat') if request.args.get('cat') else ''    # current category

    # pagination
    if request.args.get('action') == 'next':
        poffset += plimit
    elif request.args.get('action') == 'previous':
        poffset -= plimit
    elif request.args.get('action') == 'goto':
        poffset = plimit*int(request.args.get('page'))

    # show search result
    if request.method=='POST' and len(request.form.get('searchword')):
        res = getTable('products WHERE name LIKE "%'+request.form.get('searchword')+
        '%" OR prodID LIKE "%'+request.form.get('searchword')+'%"')
        numberofpages = 0
        numberofitems = fetchone('SELECT COUNT(prodID) FROM products WHERE status=0 AND \
            name LIKE "%'+request.form.get('searchword')+
        '%" OR prodID LIKE "%'+request.form.get('searchword')+'%"')[0]
    else:
        # get category
        if request.args.get('cat'):
            res = fetchall('SELECT * FROM products WHERE status=0 AND category={} LIMIT {} OFFSET {}'.format(
                request.args.get('cat'),
                plimit,
                poffset
            ))
            numberofitems = fetchone('SELECT COUNT(prodID) FROM products WHERE status=0 AND category={}'.format(
                request.args.get('cat'),
            ))[0]
            numberofpages = math.ceil(int(fetchone('SELECT COUNT(prodID) FROM products WHERE status=0 AND category={}'.format(
                request.args.get('cat'),
            ))[0])/plimit)
        else:
            # Fetch all rows from product-table
            res = fetchall('SELECT * FROM products WHERE status=0 LIMIT {} OFFSET {}'.format(
                plimit,
                poffset
            ))
            numberofitems = fetchone('SELECT COUNT(prodID) FROM products WHERE status=0')[0]
            numberofpages = math.ceil(int(fetchone('SELECT COUNT(prodID) FROM products WHERE status=0')[0])/plimit)

    return render_template('index.html', prod = res, cats=categories, currcat=cat,
    poffset=poffset, noOfItems=numberofitems, noOfPages=numberofpages, plimit=plimit)


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
    addqty = int(request.args.get('qty'))

    if request.args.get('action') == 'incqty':
        addqty+=1
        return redirect(url_for('product', id=request.args.get('id'), qty=addqty))
    elif request.args.get('action') == 'decqty' and addqty>0:
        addqty-=1
        return redirect(url_for('product', id=request.args.get('id'), qty=addqty))

    ## SUBMITTING REVIEWS ##
    if request.method=='POST':
        prodID = item[0]
        custID = str(session['userid'])
        text = form.text.data
        stars = form.stars.data
        attr = 'prodID, custID, text, stars'
        val = '%s, %s, "%s", %s' %(prodID, custID, text, stars)
        insertTo('reviews', attr, val)
        flash('Thank you for leaving a review!', 'success')
        return redirect(url_for('product', id=item[0], qty=1))
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
    qty = str(request.args.get('qty')) if request.args.get('qty') else str(request.args.get('qty'))   # quantity
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

    #  getting cart
    attr = 'cart.prodID, products.name, products.price, cart.qty, products.discount, products.img'
    join = 'products ON cart.prodID = products.prodID'
    cond = 'cart.custID = '+str(session['userid'])
    cart = innerJoin('cart', attr, join, cond)
    # cart = fetchall('SELECT * FROM view_cart WHERE custno={}'.format(
    #     session['userid']
    # ))
    lenofcart = len(cart)

    # calculate the total amount of the cart
    totalamount = 0
    totaldiscount = 0
    for items in cart:
        totaldiscount += int(items[2]*((items[4])/100))*int(items[3])
        totalamount += int(items[2]*((100-items[4])/100))*int(items[3])
    
    return render_template('cart.html', cart = cart, lenofcart=lenofcart,\
        totalamount=totalamount, totaldiscount=totaldiscount)

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
        # checkout cart with transaction
        if checkoutcart(custno=session['userid'], cart=cart):
            flash('Thank you for placing your order!', 'success')
        else:
            flash('Something went wrong, please contact system admin.', 'danger') 

    return redirect(url_for('index'))

## ORDER PAGE ##
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.', 'danger')
        return redirect('/login')
    
    # current filter tracker
    currentFilter = request.args.get('filter')

    # getting customers orders information
    # order filter
    orderFilters = {
        'all': 'SELECT `orderno`, `date`, `amount`, `status` FROM view_orders \
            WHERE custno={} ORDER BY orderno ASC'.format(session['userid']),
        'new': 'SELECT `orderno`, `date`, `amount`, `status` FROM view_orders \
            WHERE custno={} AND statuscode=0 ORDER BY orderno ASC'.format(session['userid']),
        'confirmed': 'SELECT `orderno`, `date`, `amount`, `status` FROM view_orders \
            WHERE custno={} AND statuscode=1 ORDER BY orderno ASC'.format(session['userid']),
        'delivered': 'SELECT `orderno`, `date`, `amount`, `status` FROM view_orders \
            WHERE custno={} AND statuscode=2 ORDER BY orderno ASC'.format(session['userid'])
        }
        
    # show all orders if no filter
    if currentFilter:
        queary = orderFilters.get(currentFilter)
        if currentFilter == 'confirmed':
            cond='custID={} AND status=1'.format(session['userid'])
        elif currentFilter == 'delivered':
            cond='custID={} AND status=2'.format(session['userid'])
        else:
            cond='custID={} AND status=0'.format(session['userid'])
    else:
        queary = orderFilters.get('new')
        cond='custID={} AND status=0'.format(session['userid'])

    totalamount = getSum(table='orders', column='amount', condition=cond)
    if totalamount[0] == None:
        totalamount = [0.0]

    orders = fetchall(queary)

    # getting order rows
    orderln = ''
    itemCount = ''
    if request.args.get('show') == 'order':
        ordno = request.args.get('ordno')
        orders = fetchone('SELECT * FROM view_orders WHERE orderno={}'.format(ordno))
        orderln = fetchall('SELECT p.img, o.prodID, p.name, o.qty, p.price, o.confirmed_qty, o.discount \
            FROM orderln as o INNER JOIN products as p ON o.prodID = p.prodID \
            WHERE o.orderID={}'.format(ordno))
        itemCount = fetchone('SELECT COUNT(prodID) FROM orderln WHERE orderID={}'.format(ordno))

    # search order
    if request.method == 'POST' and request.args.get('action') == 'search':
        # check if more than one search word
        sw = request.form.get('sw').split(' ')
        print(len(sw))
        for w in sw:
            orders = fetchall('SELECT * FROM view_orders WHERE orderno LIKE "%{0}%" OR custno LIKE "%{0}%" \
            OR fname LIKE "%{0}%" or lname LIKE "%{0}%"'.format(w))

    # delete order
    if request.args.get('action') == 'deleteorder':
        if deleteOrder(ordno=request.args.get('ordno')):
            flash('Order {} has been removed!'.format(request.args.get('ordno'), 'success'))
        else:
            flash('Could not remove order {}. Please contact system admin.'.format(
                request.args.get('ordno')), 'danger')
        return redirect(url_for('orders', filter=currentFilter))

    return render_template('orders.html', orders=orders, orderln=orderln,
    totalamount=totalamount, currFilter=currentFilter, itemCount=itemCount)

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

    # product categories
    cats = fetchall('SELECT textid, text FROM text WHERE typeid=1')

    # add new cat function
    if request.method == 'POST' and request.args.get('action') == 'addnewcat':
        # get highest textid
        textid = fetchone('SELECT textid FROM text WHERE typeid=1 ORDER BY textid DESC LIMIT 1')[0]+1
        commit('INSERT INTO text (typeid, type, textid, text) VALUES(1, "cat", {}, "{}")'.format(
            textid,
            request.form.get('newcat')
        ))
        flash('New category, {} has been added.'.format(
            request.form.get('newcat')
        ), 'success')
        return redirect(url_for('admin_products'))
    
    # delete category
    if request.args.get('action') == 'deletecat':
        commit('DELETE FROM text WHERE typeid=1 and text="{}"'.format(
            request.args.get('cat')
        ))
        flash('Category {} has been removed.'.format(
            request.args.get('cat')
        ), 'success')
        return redirect(url_for('admin_products'))
    
    # initialize searchbar
    form = adminProdSearch()

    # search by item number or product name
    if request.method=='POST' and request.args.get('action') == 'search':
        searchWord = str(form.search.data)
        res = getTable('products WHERE name LIKE "%'+searchWord+
        '%" OR prodID LIKE "%'+searchWord+'%"')
    else:
        res = getTable('products')      # default "show all products"

    # error message on search
    if len(res) == 0:
        flash('Your search "'+form.search.data+'" did not match any product(s).', 'warning')

    return render_template('admin/products.html', form=form, prod=res, p=page, cats=cats)

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

## ADMIN - ACTIVATE/INACTIVATE PRODUCT FUNCTION ##
@app.route('/admin/product/status')
def admin_products_status():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    # change product status
    if request.args.get('action') == 'set':
        if request.args.get('status') == 'activate':
            commit('UPDATE products SET status=0 WHERE prodID={}'.format(
                request.args.get('id')
            ))
            flash('Item {} is now active.'.format(request.args.get('id')), 'success')
        elif request.args.get('status') == 'deactivate':
            commit('UPDATE products SET status=1 WHERE prodiD={}'.format(
                request.args.get('id')
            ))
            flash('Item {} is now inactive.'.format(request.args.get('id')), 'success')

    return redirect(url_for('admin_products'))

## ADMIN - ADD/EDIT CATEGORY ##
@app.route('/admin/product/category')
def admin_products_category():
        # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    cats = fetchall('SELECT texttype, text FROM text WHERE typeid=1')

## ADMIN - ORDER PAGES ##
@app.route('/admin/orders', methods=['POST', 'GET'])
def admin_orders():
    # denies access to admin pages if not admin
    if 'userid' not in session or session['userid'] != 1891:
        flash('Permission denied!', 'danger')
        return redirect('/')
    
    currentFilter = request.args.get('filter')

    # order filter
    orderFilters = {
        'all': 'SELECT * FROM view_orders',
        'new': 'SELECT * FROM view_orders WHERE statuscode=0',
        'confirmed': 'SELECT * FROM view_orders WHERE statuscode=1',
        'delivered': 'SELECT * FROM view_orders WHERE statuscode=2'
        }

    # show all orders if no filter
    if request.args.get('filter'):
        queary = orderFilters.get(request.args.get('filter'))
    else:
        queary = orderFilters.get('new')

    orders = fetchall(queary)

    # show selected order
    orderln = ''
    if request.args.get('show') == 'order':
        ordno = request.args.get('ordno')
        orders = fetchone('SELECT * FROM view_orders WHERE orderno={}'.format(ordno))
        orderln = fetchall('SELECT p.img, o.prodID, p.name, o.qty, p.stock, o.confirmed_qty \
            FROM orderln as o INNER JOIN products as p ON o.prodID = p.prodID \
            WHERE o.orderID={}'.format(ordno))

    # search order
    searchform = adminProdSearch()
    if request.method == 'POST' and request.args.get('action') == 'search':
        # check if more than one search word
        sw = request.form.get('sw').split(' ')
        print(len(sw))
        for w in sw:
            orders = fetchall('SELECT * FROM view_orders WHERE orderno LIKE "%{0}%" OR custno LIKE "%{0}%" \
            OR fname LIKE "%{0}%" or lname LIKE "%{0}%"'.format(w))

    # confirming order using transaction
    if request.method=='POST' and request.args.get('action') == 'confirmorder':
        ordno = request.args.get('ordno')
        if confirm_order(orderno=ordno, orderlns=request.form):
            flash('Order {} is confirmed.'.format(ordno), 'success')
        else:
            flash('Cannot confirm order. Contact system admin for more info.', 'danger')
        return redirect(url_for('admin_orders', filter=currentFilter))

    # deliver order
    if request.args.get('action') == 'delivered':
        # get the latest invoice number
        inv_no = fetchone('select invoiceno from orders order by invoiceno desc limit 1')[0]+1
        ordno = request.args.get('ordno')
        # change orderstatus to "delivered"
        commit('UPDATE orders SET invoiceno={}, status=2 WHERE orderID={}'.format(inv_no, ordno))
        flash('Order {} has been delivered.'.format(ordno), 'success')
        return redirect(url_for('admin_orders', filter=currentFilter))
    
    # delete order
    if request.args.get('action') == 'deleteorder':
        if deleteOrder(ordno=request.args.get('ordno')):
            flash('Order {} has been removed!'.format(request.args.get('ordno'), 'success'))
        else:
            flash('Could not remove order {}. Please contact system admin.'.format(
                request.args.get('ordno')), 'danger')
        return redirect(url_for('admin_orders', filter=currentFilter))

    return render_template('admin/orders.html', orders=orders, orderln=orderln, 
    currFilter=currentFilter, form=searchform)

## DATE FORMAT FUNCTION ##
@app.template_filter()
def dateFormat(data):
    # value = '{:.10}'.format(str(data))
    return '{:.16}'.format(str(data))

## CURRENCY FORMAT FUNCTION ##
@app.template_filter()
def currencyFormat(value):
    return '{:,.2f} SEK'.format(float(value))

## CATEGORY FORMAT FUNCTION ##
@app.template_filter()
def catFilter(data):
    itemcount = fetchone('SELECT COUNT(prodID) FROM products WHERE status=0 AND category={}'.format(
        data
    ))[0]
    return '({})'.format(itemcount)

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
                profile_pic = str(filename)

            else:
                flash('File Extention Is Not Allowed', 'success')


        fname = str(form.first_name.data)
        lname = str(form.last_name.data)
        email = str(form.email.data)
        hashed_password = str(generate_password_hash(form.password.data))
        addr = str(form.home_address.data)
        pcode = str(form.post_code.data)
        country = form.country.data
        phone = str(form.phone_number.data)
        update = 'a.firstname="%s", a.lastname="%s", a.email="%s", a.password="%s",a.address="%s", a.postcode="%s", a.country="%s",a.phoneno="%s", a.profilepic="%s"' %(fname, lname, email, hashed_password, addr, pcode, country, phone, profile_pic)
        cond = 'custID = %s' %(data[0])

        updateAll('customers as a', update, cond)

        flash('Your Account Info Has Been Updated!', 'success')
        return redirect(url_for('customerMypage'))

    image_file = url_for('static', filename='resources/' + profile_pic)

    return render_template('customerMypage.html', image_file=image_file, form=form, data=data)

if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0', port=5000)
