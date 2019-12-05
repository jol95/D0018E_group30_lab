from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES

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

class ReviewForm(FlaskForm):
    stars = RadioField('Rate', choices=[('1',''),('2',''), ('3',''), ('4',''), ('5','')], default='3', validators=[DataRequired()])
    text = TextAreaField('', validators=[DataRequired()])

    submit = SubmitField('Submit Review')
    
class adminProdSearch(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('search')

class adminProdEdit(FlaskForm):
    images = UploadSet('images', IMAGES)
    name = StringField('Name', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    img = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!'),
        DataRequired()
    ])
    stock = IntegerField('Stock', validators=[DataRequired()])
    cat = StringField('Category', validators=[DataRequired()])
    discount = DecimalField('Discount', validators=[DataRequired()])

    submit = SubmitField('Update')
