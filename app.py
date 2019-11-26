from flask import *
from flask_mysqldb import MySQL
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from SQLfunctions import *

mysql = MySQL()
app = Flask(__name__)

app.config['SECRET_KEY'] = 'bdb878ef8ea259ef877a3686726cf4f9'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DATABASE_DB'] = 'webshop'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/products")
def products():
    args = request.args
    item = getRow('products', 'prodID=' + args.get("id"))
    return render_template('products.html', item=item)

#flash(f'Account created for {form.email.data}!', 'success')
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO customers (firstname,lastname,email, password, address, postcode, country, phoneno) VALUE(%s,%s,%s,%s,%s,%s,%s, %s)', (form.first_name.data,form.last_name.data,form.email.data,form.password.data,form.home_address.data,form.post_code.data,form.country.data,form.phone_number.data ))
        mysql.connection.commit()
        #flash(f'Account created for {form.email.data}!', 'success')
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


@app.route('/addtocart')
def addtocart():
    # redirect user to login page if not logged in
    if 'userid' not in session:
        flash('Please log in or create an account.')
        return redirect('/login')

    # attribute data for shoping cart
    custID = str(session['userid'])  # temporary customer ID (unregistred user)
    prodID = str(request.args.get('id'))  # productID
    qty = str(request.args.get('qty'))  # quantity
    cond = 'custID = ' + custID + ' AND prodID = ' + prodID  # insert/update condition

    # check if the product already exists in users cart
    if exist('cart', cond):
        inCart = getRow('cart', cond)
        # increase the quantity of existing product
        addqty = str(int(inCart[3]) + int(qty))
        updateIn('cart', 'qty', addqty, cond)
    else:
        # add new product to the cart
        attr = 'custID, prodID, qty'
        values = '%s, %s, %s' % (custID, prodID, qty)
        insertTo('cart', attr, values)

    flash('Product has been added to the shopping cart.')
    return redirect('/product?id=' + prodID)

@app.route('/startsess')
def startsess():
    session['userid'] = 1891
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
