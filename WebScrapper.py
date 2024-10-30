from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import re
import pandas as pd
from io import BytesIO
from PIL import Image
from constants import DRIVER_EXECUTABLE_NAME

class WebScrapper:
    def __init__(self,curr_dir):
        #Set up directory and paths
        self.curr_dir = curr_dir
        self.chrome_driver_path = os.path.join(self.curr_dir, DRIVER_EXECUTABLE_NAME)

        #Set up constants
        self.left_padding = 300
        self.top_padding = 60
        self.right_padding = 100
        self.bottom_padding = 0

        # Set up Chrome options
        """
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.curr_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        })
        self.driver = webdriver.Chrome(service=Service(self.chrome_driver_path), options=self.chrome_options)
        """

        #initializing selenium webdriver
        self.driver = webdriver.Chrome(service=Service(self.chrome_driver_path))
        self.driver.set_window_size(1200, 800)

    def getDriver(self,url):
        return self.driver.get(url)
    
    def getElementByID(self,id):
        return self.driver.find_element(By.ID,id)

    def getWaitElementByID(self,id):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, id))
            )
            return element
        except ValueError as e:
            print(e)
            print("Error in parsing wait element id : ${}".format(id))

    def capture_image_element(self, img_element):
        screenshot_png = self.driver.get_screenshot_as_png()
        full_image = Image.open(BytesIO(screenshot_png))
        location = img_element.location
        size = img_element.size
        left = int(location['x']) + self.left_padding
        top = int(location['y']) + self.top_padding
        right = int(left + size['width']) + self.right_padding
        bottom = int(top + size['height']) + self.bottom_padding
        return full_image.crop((left, top, right, bottom))

    def get_dict_from_web_page_table(self, table):
        headers = [header.text.replace("\n"," ") for header in table.find_elements(By.TAG_NAME, 'th')]
        rows = []
        for row in table.find_elements(By.TAG_NAME, 'tr')[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = [cell.text for cell in cells]
            rows.append(row_data)
        return pd.DataFrame(rows, columns=headers).to_dict(orient='records')
    
    def wait_for_table(self, table_id, max_retries=3):
        for attempt in range(max_retries):
            try:
                return WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, table_id))
                )
            except Exception:
                print(f"Attempt {attempt + 1}: {table_id} not found. Retrying...")
                time.sleep(1)  # Optional: wait before retrying
        raise ValueError(f"Failed to find {table_id} after multiple attempts.")

    def driver_close(self):
        self.driver.quit()