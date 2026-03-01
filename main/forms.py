"""
This file has the forms for our flask website
"""

# Import necessary components for form handling in Flask
from flask_wtf import FlaskForm  # Base class for creating secure web forms
from wtforms import StringField, PasswordField, SubmitField, BooleanField  # Standard input fields
from wtforms.fields.numeric import IntegerField  # Numeric input field
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange  # Validation utilities

from main.models import User  # Import the User model for database interaction

# Form for user registration with fields for username, password, and password confirmation
class RegistrationForm(FlaskForm):
    email = StringField('Email Address',
                           validators=[DataRequired(), Length(min=2, max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already taken, please login instead.")


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Form for creating a sell order with fields for units and price per unit
class SellOrderForm(FlaskForm):
    unit = IntegerField('Units', validators=[DataRequired()])  # Number of units to sell
    price = IntegerField('Price Per unit', validators=[DataRequired()])  # Price per unit
    submit = SubmitField('Sell Units')  # Submit button


# Form for purchasing units with validation for non-negative numbers
class PurchaseForm(FlaskForm):
    units = IntegerField('Units', validators=[DataRequired(), NumberRange(0)])  # Units to purchase (must be >= 0)
    submit = SubmitField('Buy')  # Submit button

# Form for generating energy
class GenerateEnergyForm(FlaskForm):
    kwh = IntegerField('Energy Generated (kWh)', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Generate Energy')
