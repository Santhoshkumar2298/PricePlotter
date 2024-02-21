import os
import random
import time
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
import smtplib

load_dotenv()
MY_EMAIL = os.getenv('MY_EMAIL')
MY_PASSWORD = os.getenv('MY_PASSWORD')


async def fetch_html(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def extract_price(html, site):
    soup = BeautifulSoup(html, 'html.parser')
    if site.lower() == "amazon":
        try:
            price_element = soup.find(class_='a-price-whole')
            return price_element.text.replace(",", "") if price_element else False
        except Exception as e:
            print(str(e))
            return False
    elif site.lower() == "flipkart":
        try:
            price_element = soup.find(class_='_30jeq3')
            return price_element.text.strip("₹").replace(",", "") if price_element else False
        except Exception as e:
            print(str(e))
            return False


async def check_valid_url(url, site):
    try:
        html = await fetch_html(url)
        price = await extract_price(html, site)
        return price
    except Exception as e:
        print(f"Error fetching price: {str(e)}")
        return False


# def check_valid_url(url, site):
#     edge_options = EdgeOptions()
#     # edge_options.add_argument("--headless")
#     edge_options.add_argument('--enable-javascript')
#     edge_options.add_experimental_option("detach", True)
#     driver = webdriver.Edge(options=edge_options)
#     driver.get(url)
#
#     time.sleep(3)
#
#     if site.lower() == "amazon":
#         try:
#             time.sleep(7)
#             price = driver.find_element(By.CLASS_NAME, 'a-price-whole')
#             price = price.text.replace(",", "")
#             return price
#         except Exception as e:
#             print(str(e))
#             return False
#         except TimeoutError:
#             return "TimeOut"
#
#     elif site.lower() == "flipkart":
#         try:
#             time.sleep(7)
#             price = driver.find_element(By.CLASS_NAME, '_30jeq3')
#             stripped_price = price.text.strip("₹")
#             stripped_price = stripped_price.replace(",", "")
#             return stripped_price
#         except Exception as e:
#             print(str(e))
#             return False
#         except TimeoutError:
#             return "TimeOut"
#     driver.quit()


# FOR UDEMY IN CASE

# elif site == "udemy":
#     try:
#         driver = webdriver.Edge()
#         driver.get(url)
#         time.sleep(5)
#         price = driver.find_element(By.XPATH,
#             "//div[@class='base-price-text-module--container--2P5fs ud-clp-price-text']
#             //div[@class='base-price-text-module--price-part--3AFBv base-price-text-module--original
#             -price--3kPJa ud-clp-list-price ud-text-sm']//span[@class='ud-sr-only']/following-sibling::span//span")
#         print(price)
#         return True
#     except Exception as e:
#         print(str(e))
#         return False

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
