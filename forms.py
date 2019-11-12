from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
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
    password = PasswordField('Password', validatords=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')
