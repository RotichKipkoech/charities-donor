from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CharityApplicationForm(FlaskForm):
    name = StringField('Charity Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[Length(max=200)])
    submit = SubmitField('Apply')
