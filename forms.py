from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(message="Invalid Email Address")])
    password = PasswordField(label="Password", validators=[DataRequired()])
    login = SubmitField(label="LogIn")


class SignUpForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired(), Email(message="Invalid Email Address")])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8, max=15,
                                                                                  message="Password should between 8 to"
                                                                                          "15 characters")])
    confirm_pass = PasswordField(label="Confirm Password", validators=[DataRequired(), EqualTo("password",
                                                                                               message="Password Not "
                                                                                                       "Match")])
    signup = SubmitField(label="Sign Up")


class ForgotForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(message="Invalid Email Address")])
    otp = StringField(label="Enter OTP", validators=[DataRequired(), Length(min=6, max=6, message="Invalid OTP")])
    new_pass = PasswordField(label="New Password", validators=[DataRequired(), Length(min=8, max=15,
                                                                                      message="Password should "
                                                                                              "between 8 to 15 "
                                                                                              "characters")])
    new_cpass = PasswordField(label="Confirm New Password", validators=[DataRequired(), EqualTo("new_pass",
                                                                                                message="Password Not "
                                                                                                        "Match")])

    send_otp = SubmitField(label="Send OTP", name="send_otp")
    submit_otp = SubmitField(label="Submit",  name="submit_otp")
    submit_pass = SubmitField(label="Submit",  name="submit_pass")
    show_send_otp = False
    show_submit_otp = False
    show_submit_pass = False


class AddItemForm(FlaskForm):
    product_name = StringField(label="Product Name", validators=[DataRequired()])
    site_name = SelectField(label="Select Site",
                            choices=[("amazon", "Amazon"), ("flipkart", "Flipkart")])
    product_url = StringField(label="Product URL",
                              validators=[DataRequired(), URL(require_tld=True, message="Invalid URL")])
    target_price = StringField(label="Target Price", validators=[DataRequired()])
    add_btn = SubmitField(label="Add")
    update_btn = SubmitField(label="Update")


class ProfileForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email (for Alerts and Signin)",
                        validators=[DataRequired(), Email(message="Invalid Email Address")])
    feedback = TextAreaField(label="Feedback (optional)")
    update_btn = SubmitField(label="Update")
