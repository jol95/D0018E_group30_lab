<<<<<<< HEAD
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'bdb878ef8ea259ef877a3686726cf4f9'


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/products")
def about():
    return render_template('products.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
app = Flask(__name__)

#MYSQL CONNECTION SETTINGS

# app.config['MYSQL_HOST'] = 'sql7.freemysqlhosting.net'
# app.config['MYSQL_USER'] = 'sql7311847'
# app.config['MYSQL_PASSWORD'] = '5h2gDVdPYS'
# app.config['MYSQL_DB'] = 'sql7311847'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config['MYSQL_HOST'] = 'gr30db.database.windows.net'
app.config['MYSQL_PORT'] = 1433
app.config['MYSQL_USER'] = 'gr30adm'
app.config['MYSQL_PASSWORD'] = 'Choss!95'
app.config['MYSQL_DB'] = 'gr30db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
	cur = mysql.connection.cursor()
	cur.execute('''CREATE TABLE example (id INTEGER, name VARCHAR(20))''')
	return 'done'

if __name__ == "__main__":
	app.run(debug = True)
>>>>>>> aws key added
