from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField, TextAreaField, FileField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    home_address = StringField('Home Address', validators=[DataRequired()])
    post_code = StringField('Post Code', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])

    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')

class adminProdSearch(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('search')

class adminProdEdit(FlaskForm):
    name = StringField('Name')
    desc = TextAreaField('Description')
    price = IntegerField('Price')
    img = FileField('Image')
    stock = IntegerField('Stock')
    cat = StringField('Category')
    discount = DecimalField('Discount')

    submit = SubmitField('Update')


class customerMypageform(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    home_address = StringField('Home Address', validators=[DataRequired()])
    post_code = StringField('Post Code', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')


class ReviewForm(FlaskForm):
    text = TextAreaField('', validators=[DataRequired()])

    submit = SubmitField('Submit Review')


