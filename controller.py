import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By
import smtplib

load_dotenv()
MY_EMAIL = os.getenv('MY_EMAIL')
MY_PASSWORD = os.getenv('MY_PASSWORD')


def check_valid_url(url, site):
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")
    edge_options.add_argument('--enable-javascript')
    edge_options.add_experimental_option("detach", True)
    edge_options.use_chromium = True
    driver = webdriver.Edge(edge_options)
    driver.get(url)

    if site.lower() == "amazon":
        try:
            time.sleep(3)
            price = driver.find_element(By.CLASS_NAME, 'a-price-whole')
            price = price.text.replace(",", "")
            return price
        except Exception as e:
            print(str(e))
            return False
        except TimeoutError:
            return "TimeOut"

    elif site.lower() == "flipkart":
        try:
            time.sleep(3)
            price = driver.find_element(By.CLASS_NAME, '_30jeq3')
            stripped_price = price.text.strip("₹")
            stripped_price = stripped_price.replace(",", "")
            return stripped_price
        except Exception as e:
            print(str(e))
            return False
        except TimeoutError:
            return "TimeOut"
    driver.quit()


def mail_price_alert(price, email, product_name):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=email,
                            msg=f"Subject: Price Drop Alert ! - Price Plotter\n\n There is a price drop of one of "
                                f"your desired product {product_name} with the current price Rs. {price}. \n\nHurry "
                                f"Up !")


def send_feedback(message, username, user_email):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL,
                            msg=f"Subject: Feedback from {username} - Price Plotter\n\n {message} \n\n"
                                f"Username : {username}\nEmail : {user_email}")


def send_otp(email, otp):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=email,
                            msg=f"Subject: Reset Password Request OTP - Price Plotter\n\n OTP : {otp}")
