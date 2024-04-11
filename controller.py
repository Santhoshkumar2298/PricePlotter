import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import smtplib
import requests

load_dotenv()
MY_EMAIL = os.getenv('MY_EMAIL')
MY_PASSWORD = os.getenv('MY_PASSWORD')


# def check_valid_url(url, site):
#     edge_options = EdgeOptions()
#     edge_options.add_argument("--headless")
#     edge_options.add_argument('--enable-javascript')
#     edge_options.add_experimental_option("detach", True)
#     edge_options.use_chromium = True
#     driver = webdriver.Edge(edge_options)
#     driver.get(url)
#
#     if site.lower() == "amazon":
#         try:
#             time.sleep(3)
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
#             time.sleep(3)
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

def check_valid_url(url, site):
    # if site.lower() == "amazon":
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/123.0.0.0",
    #         'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    #         'Origin': "https://www.amazon.in",
    #         'Referer': "https://www.amazon.in/"
    #     }
    #     response = requests.get(url, headers=headers)
    #     time.sleep(3)
    #     soup = BeautifulSoup(response.content, 'html5lib')
    #     print(soup.prettify())
    #     try:
    #         price = soup.findall('div')
    #         print(price)
    #
    #         # price_text = price.get_text(strip=True)
    #         # print(price_text)
    #         # return price_text.strip(".")
    #     except Exception as e:
    #         print(f"Error: {str(e)}")
    #         return False

    if site.lower() == "flipkart":
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': "https://www.flipkart.com/",
            'Referer': "https://www.flipkart.com/"
        }
        response = requests.get(url, headers=headers)
        print(response.content, flush=True)
        time.sleep(4)
        soup = BeautifulSoup(response.content, 'lxml')
        print(soup.prettify(), flush=True)
        try:
            price = soup.find('div', class_='_30jeq3 _16Jk6d')
            price_text = price.get_text(strip=True)
            stripped_price = price_text.strip("₹").replace(",", "")
            return stripped_price
        except Exception as e:
            print(f"Error: {str(e)}")
            return False


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
