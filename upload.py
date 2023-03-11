import os
import time
from playwright.sync_api import sync_playwright
import logging

"""
Logger with the below function will create a log file in the current directory

logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
"""
logging.basicConfig(filename="application.log", level=logging.DEBUG)


SUCCESS = 200
USER_NAME = "enggrajesh131998@gmail.com"
PASSWORD = "Rajesh1"

CWD = os.getcwd()


class Uploader:
    def __init__(self, url):
        self.url = url
        self.product_data = {
            "title": "Test Product",
            "short_description": "Test Description",
        }

    def upload(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            time.sleep(2)
            page.locator("a >> text=Log in with username and password").click()
            page.locator("#user_login").fill(USER_NAME)
            page.locator("#user_pass").fill(PASSWORD)
            page.locator("#wp-submit").click()
            page.goto(
                "https://celebratelifestyle.in/wp-admin/post-new.php?post_type=product"
            )
            page.locator("#title").fill(self.product_data["title"])

            page.locator("#_regular_price").fill("100")
            page.locator("#_sale_price").fill("50")

            page.locator("#set-post-thumbnail").click()
            page.locator("input[type=file]").set_input_files(
                "/Users/naveensingh/projects/CLS-Web-Scrapping/data/images/2023-03-11/miima-Black-104425/1.jpg"
            )

            with page.expect_response(
                "https://celebratelifestyle.in/wp-admin/async-upload.php"
            ) as response_info:
                response = response_info.value
                print(response.status)
            page.locator("button >> text=Set product image").click()

            time.sleep(5)

            page.locator("p >> a >> text=Add product gallery images").click()
            folder = "/Users/naveensingh/projects/CLS-Web-Scrapping/data/images/2023-03-11/miima-Black-104425/"
            files = os.listdir(folder)
            files = [f"{folder}/{i}" for i in files if i.endswith(".jpg")]
            page.locator("input[type=file] >> nth=1").set_input_files(files)

            with page.expect_response(
                "https://celebratelifestyle.in/wp-admin/async-upload.php"
            ) as response_info:
                response = response_info.value
                print(response.status)

            page.locator("button >> text=Add to gallery").click()

            time.sleep(500)


if __name__ == "__main__":
    url = "https://celebratelifestyle.in/wp-admin/"
    scraper = Uploader(url)
    scraper.upload()
