import os
import random
import threading
import time
from datetime import datetime
from datetime import timedelta
import schedule
import sqlalchemy
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr
from werkzeug.security import generate_password_hash, check_password_hash
from Models import Base, User, Product
from controller import check_valid_url, mail_price_alert, send_feedback, send_otp
from features import features
from forms import LoginForm, SignUpForm, AddItemForm, ProfileForm, ForgotForm

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config["SECRET_KEY"] = os.getenv("CSRF_SECRET")

toastr = Toastr(app)

# CONNECTING DB TO THE APP
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

otp = None
user_email = None


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# TO CREATE TABLE SCHEMA IT REQUIRES APP CONTEXT
with app.app_context():
    db.create_all()


def get_current_year():
    current_year = datetime.now().year
    return current_year


@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():
    is_home = True
    logout_user()
    return render_template("homepage.html", year=get_current_year(), features=features, is_home=is_home)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            pass

        else:
            check_user = db.session.execute(db.select(User).where(User.email == f"{request.form['email']}")).scalar()

            if check_user is not None:
                if check_password_hash(check_user.password, request.form["password"]):
                    login_user(check_user)
                    return redirect(url_for("dashboard"))
                else:
                    flash("Invalid Credentials", "error")
            else:
                flash("User Not Found", "error")

    return render_template("login_page.html", year=get_current_year(), form=form)


@app.route("/login/forgot_password", methods=["GET", "POST"])
def forgot_pass():
    form = ForgotForm()
    form.show_send_otp = True
    global user_email, otp

    if request.method == "POST":
        if "send_otp" in request.form and form.is_submitted():
            user = db.session.query(User).filter(User.email == form.email.data).first()
            user_email = user.email
            if user_email:
                otp = random.randint(111111, 999999)
                send_otp(user_email, otp)
                flash("OTP is Successfully Sent", "success")
                form.show_send_otp = False
                form.show_submit_otp = True
            else:
                flash("User Not Found with this Email", "error")

        if "submit_otp" in request.form and form.is_submitted():
            if int(form.otp.data) == int(otp):
                form.show_send_otp = False
                form.show_submit_pass = True
                form.show_submit_otp = False
            else:
                flash("Incorrect OTP", "error")

        if "submit_pass" in request.form and form.is_submitted():
            if form.new_pass.data == form.new_cpass.data:
                user_data = db.session.query(User).filter(User.email == user_email).first()
                hashed_pass = generate_password_hash(form.new_pass.data, "pbkdf2", 10)
                user_data.password = hashed_pass
                db.session.commit()
                flash("Password reset Successfully", "success")
                return redirect(url_for("login"))
            else:
                flash("Password not match. OTP Expired", "error")

    return render_template("login_page.html", is_forgot_pass=True, form=form, year=get_current_year())


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            pass
        if form.is_submitted():
            if request.form["username"] != "" and request.form["password"] != "" and request.form["email"] != "" and \
                    request.form["confirm_pass"] != "":

                hashed_pass = generate_password_hash(request.form["password"], "pbkdf2", 10)

                new_user = User(
                    username=request.form["username"].title(),
                    password=hashed_pass,
                    email=request.form["email"]
                )
                try:
                    db.session.add(new_user)
                    db.session.commit()

                    flash("Registered Successfully", 'success')

                    return redirect(url_for("login"))
                except sqlalchemy.exc.IntegrityError:
                    flash("Username or Email Id already Found", 'error')

    return render_template("signup.html", year=get_current_year(), form=form)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/analytics", methods=["GET"])
@login_required
def analytics():
    user_products = db.session.query(Product).where(Product.user_id == current_user.id).all()
    return render_template("track_analytics.html", product_list=user_products)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_settings():
    form = ProfileForm()
    user_data = db.get_or_404(User, current_user.id)

    if request.method == "GET":
        form.username.data = user_data.username
        form.email.data = user_data.email
        form.feedback.data = ""

    if request.method == "POST" and form.validate_on_submit():
        if form.is_submitted():
            user_data.username = form.username.data
            user_data.email = form.email.data
            db.session.commit()

            if form.feedback.data != "":
                send_feedback(message=form.feedback.data, username=user_data.username, user_email=user_data.email)
                flash(f"Thanks for Your Feedback, {user_data.username} and your data updated successfully", "success")
                return redirect(url_for("profile_settings"))
            else:
                flash("Data Updated Successfully", "success")
                return redirect(url_for("profile_settings"))

    return render_template("profile.html", form=form)


@app.route("/analytics/add", methods=["GET", "POST"])
@login_required
async def add_items():
    form = AddItemForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            pass

        if (request.form["product_name"] != "" and request.form["product_url"] != "" and
                request.form["target_price"] != ""):

            if request.form["site_name"].lower() in request.form["product_url"]:
                try:
                    product_price = await check_valid_url(request.form["product_url"],
                                                          request.form["site_name"].lower())

                    if not product_price:
                        flash("Invalid URL", "warning")
                    else:
                        new_product = Product(
                            product_name=request.form["product_name"].title(),
                            site_name=request.form["site_name"].title(),
                            product_url=request.form["product_url"],
                            product_price=product_price,
                            current_price=product_price,
                            target_price=request.form["target_price"],
                            user_id=current_user.id
                        )

                        db.session.add(new_product)
                        db.session.commit()
                        flash("Product Added for tracking Successfully", "success")
                    return redirect(url_for("analytics"))
                except Exception as e:
                    print(f"Error : {str(e)}")
            else:
                flash("Site Name and Url is Mismatch", "warning")

    return render_template("add_items.html", form=form)


# def add_items():
#     form = AddItemForm()
#
#     if request.method == "POST":
#         if not form.validate_on_submit():
#             pass
#
#         if (request.form["product_name"] != "" and request.form["product_url"] != "" and
#                 request.form["target_price"] != ""):
#
#             if request.form["site_name"].lower() in request.form["product_url"]:
#                 try:
#                     product_price = check_valid_url(request.form["product_url"], request.form["site_name"].lower())
#
#                     if product_price == "TimeOut":
#                         flash("Server is Not Responding, Please try later", "error")
#                     elif not product_price:
#                         print(product_price)
#                         flash("Invalid URL", "warning")
#                     else:
#                         new_product = Product(
#                             product_name=request.form["product_name"].title(),
#                             site_name=request.form["site_name"].title(),
#                             product_url=request.form["product_url"],
#                             product_price=product_price,
#                             current_price=product_price,
#                             target_price=request.form["target_price"],
#                             user_id=current_user.id
#                         )
#
#                         db.session.add(new_product)
#                         db.session.commit()
#                         flash("Product Added for tracking Successfully", "success")
#                     return redirect(url_for("analytics"))
#                 except Exception as e:
#                     print(f"Error : {str(e)}")
#             else:
#                 flash("Site Name and Url is Mismatch", "warning")
#
#     return render_template("add_items.html", form=form)


@app.route("/analytics/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_item(product_id):
    product_data = db.get_or_404(Product, product_id)

    edit_form = AddItemForm(
        product_name=product_data.product_name,
        product_url=product_data.product_url,
        site_name=product_data.site_name,
        target_price=product_data.target_price
    )

    if request.method == "POST" and edit_form.validate_on_submit():
        if (request.form["product_name"] != "" and request.form["site_name"] != "" and
                request.form["target_price"] != ""):
            product_data.product_name = edit_form.product_name.data.title()
            product_data.product_url = edit_form.product_url.data
            product_data.site_name = edit_form.site_name.data.title()
            product_data.target_price = edit_form.target_price.data

            db.session.commit()
            flash("Edited Successfully", "success")
            return redirect(url_for("analytics"))
    return render_template("add_items.html", form=edit_form, id=product_data.id, is_edit=True)


@app.route("/delete/<int:product_id>", methods=["GET"])
@login_required
def delete_item(product_id):
    item = db.get_or_404(Product, product_id)
    db.session.delete(item)
    db.session.commit()
    flash("Product Deleted Successfully", "success")
    return redirect(url_for("analytics"))


@app.route("/track_status/<int:product_id>/<string:toggle>", methods=["GET"])
@login_required
def track_status(product_id, toggle):
    item = db.get_or_404(Product, product_id)
    if toggle == "on":
        item.track_status = True
    if toggle == "off":
        item.track_status = False
    db.session.commit()

    return redirect(url_for("analytics"))


@app.route("/track_status/<int:product_id>/sync", methods=["GET"])
def sync_now(product_id):
    item = db.get_or_404(Product, product_id)
    current_price = check_valid_url(item.product_url, item.site_name)

    if current_price == "TimeOut":
        flash("Server is Not Responding, Please try later", "error")
    else:
        item.current_price = current_price
        db.session.commit()

        if int(item.current_price) <= int(item.target_price):
            user_mail = db.get_or_404(User, current_user.id).email
            product_name = item.product_name
            mail_price_alert(item.current_price, user_mail, product_name)

    return redirect(url_for("analytics"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


def update_price():
    items = db.session.query(Product).all()
    for item in items:
        if item.track_status:
            current_price = check_valid_url(item.product_url, item.site_name)

            if current_price == "TimeOut":
                flash("Server is Not Responding, Please try later", "error")
            else:
                item.current_price = current_price
                db.session.commit()

                if int(item.current_price) <= int(item.target_price):
                    user_mail = db.get_or_404(User, current_user.id).email
                    product_name = item.product_name
                    mail_price_alert(item.current_price, user_mail, product_name)


def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at("06:00").do(update_price)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    app.run(debug=True)
