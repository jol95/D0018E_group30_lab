from flask import Flask, render_template, url_for, flash, redirect, request
from flask_mysqldb import MySQL
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)

app.config['SECRET_KEY'] = 'bdb878ef8ea259ef877a3686726cf4f9'

app.config['MYSQL_HOST'] = 'ec2-13-53-70-153.eu-north-1.compute.amazonaws.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'webshop'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)



@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/products")
def products():
    return render_template('products.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = mysql.connect()
        cursor = conn.cursor()
        hashed_pwd = generate_password_hash(form.password.data)
        cursor.callproc('sp_createCustomer', (form.first_name.data, form.last_name.data, form.email.data, hashed_pwd, form.home_address.data, form.post_code.data, form.country.data, form.phone_number.data))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            flash(f'Account created for {form.email.data}!', 'success')
        cursor.close()
        conn.close()
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


if __name__ == '__main__':
    app.run(debug=True)
