from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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
