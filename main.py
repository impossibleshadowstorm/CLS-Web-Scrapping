import os
import time
import requests
from openpyxl import load_workbook
from datetime import datetime
from src.helpers import get_products, ImageResizer
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


HEIGHT = 620
WIDTH = 620
SUCCESS = 200
CWD = os.getcwd()


class ProductScraper:
    """
    A class for scraping product data from a URL and saving it to an Excel file.

    Args:
        product_page (str): A product URL to scrape.

    Attributes:
        product_page (str): A product URL to scrape.
        product_data (list): A list of dictionaries containing the product data to scrape.

    Methods:
        scrape: Scrapes product data from the URL in the `urls` attribute.
        get_product_data: Extracts data from a product page using CSS selectors.
        get_or_create_folder_name: Returns a folder name based on the product title or current date and time.
        save_image: Downloads an image from a URL and saves it to the specified folder.
        append_to_excel: Appends a row of product data to an existing Excel file.

    Example Usage:

    ```
    url = 'https://www.example.com/product/1'
    scraper = ProductScraper(url)
    scraper.scrape()
    ```
    """

    def __init__(self, url):
        self.url = url
        self.product_data = [
            {
                "key": "date",
                "name": "Date",
                "type": "date",
                "value": datetime.now().strftime("%Y-%m-%d"),
            },
            {
                "key": "#variation_color_name >> span >> nth=0",
                "name": "Varient",
                "type": "text",
                "value": "",
            },
            {"key": "#title", "name": "Title Section", "type": "text", "value": ""},
            {
                "key": "#corePriceDisplay_desktop_feature_div >> .a-price-whole >> nth=0",
                "name": "Price Section",
                "type": "text",
                "value": "",
            },
            {
                "key": "#corePriceDisplay_desktop_feature_div >> div >> nth=1 >> span >> nth=1",
                "name": "Regular Price Section",
                "type": "text",
                "value": "",
            },
            {
                "key": "#productOverview_feature_div >> table",
                "name": "Overview Section",
                "type": "html",
                "value": "",
            },
            {
                "key": "#prodDetails >> div >> div >> nth=0",
                "name": "Product Detail",
                "type": "html",
                "value": "",
            },
            {
                "key": "image_path",
                "name": "Image Path",
                "type": "file_path",
                "value": "",
            },
            {
                "key": "product_link",
                "name": "Product Link",
                "type": "link",
                "value": url,
            },
        ]

    def get_product_data(self, page):
        """
        Extracts data from a product page using CSS selectors.

        Args:
            page: A Playwright page object representing a product page.

        Returns:
            A list of dictionaries containing the product data.
        """
        data = self.product_data.copy()
        for item in data:
            if item["type"] == "html":
                item["value"] = page.query_selector(item["key"]).inner_html()
            elif item["type"] == "text":
                item["value"] = page.query_selector(item["key"]).inner_text()
        return data

    def get_or_create_folder_name(self, title, variant):
        now = datetime.now()
        current_time = now.strftime("%H%M%S")
        if title is not None or title != "":
            folder_name = title.replace(" ", "_").lower()
            if len(folder_name) > 5:
                folder_name = f"{folder_name[:5]}-{variant}-{current_time}"
            else:
                folder_name = f"{folder_name}-{variant}-{current_time}"
        else:
            folder_name = current_time

        dir_path = os.path.join(
            CWD, "data", "images", f"{now.strftime('%Y-%m-%d')}", folder_name
        )
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    def append_to_excel(self, filename, data):
        file_path = os.path.join(CWD, "data", filename)
        wb = load_workbook(os.path.join(CWD, "data", filename))
        ws = wb.active

        data = [item["value"] for item in data]
        ws.append(data)
        wb.save(file_path)

    def save_image(self, url, folder, idx):
        """
        Downloads an image from a URL and saves it to the specified folder.

        Args:
            url (str): The URL of the image to download.
            folder (str): The name of the folder to save the image to.
            idx (int): The index of the image in the list of images.
        """
        filename = f"{idx}.jpg"
        file_path = os.path.join(folder, filename)
        response = requests.get(url)
        if response.status_code == SUCCESS:
            with open(file_path, "wb") as file:
                file.write(response.content)
        else:
            logging.error("Error: image could not be downloaded")

    def scrape(self):
        """
        Scrapes product data from the URL in the `url` attribute and saves it to an Excel file.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            time.sleep(2)
            if page.query_selector("#imgTagWrapperId") != None:
                page.click("#imgTagWrapperId")
            else:
                page.click("#main-image-container")
            time.sleep(2)

            product_data = self.get_product_data(page)
            title = product_data[2]["value"]
            varient = product_data[1]["value"]
            folder = self.get_or_create_folder_name(title, varient)

            image_elements = page.query_selector_all("#ivThumbs >> .ivThumbImage")
            for idx, image_element in enumerate(image_elements):
                try:
                    image_element.click()
                    time.sleep(1)
                    image_tag = page.query_selector("#ivLargeImage >> img")
                    if image_tag is not None:
                        image_src = image_tag.get_attribute("src")

                        if not image_src.startswith("data:image/"):
                            self.save_image(image_src, folder, idx)
                        else:
                            logging.error("Error: image is not available")
                except Exception as e:
                    logging.error(f"Error: {e}")

            resizer = ImageResizer(HEIGHT, WIDTH)
            resizer.resize_all(folder)
            product_data[7]["value"] = folder
            self.append_to_excel("products.xlsx", product_data)
            browser.close()

    def get_all_varients(self):
        """
        Scrapes product data from the URL in the `url` attribute and saves it to an Excel file.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)

            varients = []
            varient_elements = page.query_selector_all("#variation_color_name >> li")
            for varient_element in varient_elements:
                varient_element.click()
                time.sleep(3)
                varients.append(page.url)

            browser.close()
            return varients


if __name__ == "__main__":
    product_pages = get_products()
    for product_page in product_pages:
        scrapper = ProductScraper(product_page)
        all_varients = scrapper.get_all_varients()
        for varient in all_varients:
            try:
                product_scrapper = ProductScraper(varient)
                product_scrapper.scrape()
            except Exception as e:
                logging.error("Error while scraping product: try manually {e}", exc_info=True)
                print("Could not find data for - ", varient)