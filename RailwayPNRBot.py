import os
import time
import re
import pandas as pd
from io import BytesIO
from PIL import Image
import pytesseract
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RailwaysPNRBot:
    def __init__(self):
        self.curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.tesseract_executable = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        self.chrome_driver_path = os.path.join(self.curr_dir, 'chromedriver.exe')
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_executable
        
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.curr_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        })
        self.driver = webdriver.Chrome(service=Service(self.chrome_driver_path), options=self.chrome_options)
        self.driver.set_window_size(1200, 800)

    def capture_image_element(self, img_element):
        screenshot_png = self.driver.get_screenshot_as_png()
        full_image = Image.open(BytesIO(screenshot_png))
        location = img_element.location
        size = img_element.size
        left = int(location['x']) + 300
        top = int(location['y']) + 60
        right = int(left + size['width']) + 100
        bottom = int(top + size['height'])
        return full_image.crop((left, top, right, bottom))

    def get_dict_from_web_page_table(self, table):
        headers = [header.text.replace("\n"," ") for header in table.find_elements(By.TAG_NAME, 'th')]
        rows = []
        for row in table.find_elements(By.TAG_NAME, 'tr')[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = [cell.text for cell in cells]
            rows.append(row_data)
        return pd.DataFrame(rows, columns=headers).to_dict(orient='records')

    def get_captcha_answer(self, t):
        digits = [d for d in re.split(r"\D", t) if d]
        operand = re.findall(r"\D", t)[0]
        return int(digits[0]) + int(digits[1]) if operand == '+' else int(digits[0]) - int(digits[1])

    def solve_captcha(self, captcha_id, max_retries=3):
        for attempt in range(max_retries):
            captcha_image = self.capture_image_element(captcha_id)
            captcha_text = pytesseract.image_to_string(captcha_image).strip()
            if captcha_text and re.search(r'\d', captcha_text):  # Check if digits are found
                return self.get_captcha_answer(captcha_text)
            print(f"Attempt {attempt + 1}: OCR failed. Retrying...")
            time.sleep(1)  # Optional: wait before retrying
        raise ValueError("Failed to solve CAPTCHA after multiple attempts.")

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

    def load_json_data(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def run(self, pnr, json_file_path=None, max_retries=3):
        for attempt in range(max_retries):
            self.driver.get("https://www.indianrail.gov.in/enquiry/PNR/PnrEnquiry.html?locale=en")
            print(self.driver.title)

            # Input PNR number
            self.driver.find_element(By.ID, 'inputPnrNo').send_keys(pnr)
            self.driver.find_element(By.ID, 'modal1').click()

            # Wait for CAPTCHA image to be present
            try:
                captcha_id = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, 'CaptchaImgID'))
                )
                ans = self.solve_captcha(captcha_id)
            except ValueError as e:
                print(e)
                print("Retrying the entire process...")
                continue  # Retry the whole process

            # Submit CAPTCHA answer
            self.driver.find_element(By.ID, 'inputCaptcha').send_keys(ans)
            self.driver.find_element(By.ID, 'submitPnrNo').click()

            # Wait for journey details table
            try:
                journey_details_info_table = self.wait_for_table('journeyDetailsTable')
                ticket_status_info_table = self.wait_for_table('psgnDetailsTable')
                other_details_table = self.wait_for_table('otherDetailsTable')
            except ValueError as e:
                print(e)
                print("Retrying the entire process...")
                continue  # Retry the whole process

            # If all is successful, extract data
            data = {
                'journeyDetailsInfo': self.get_dict_from_web_page_table(journey_details_info_table)[0],
                'ticketStatusInfo': self.get_dict_from_web_page_table(ticket_status_info_table)[0],
                'otherDetails': self.get_dict_from_web_page_table(other_details_table)[0]
            }

            # Load additional JSON data if provided
            if json_file_path:
                try:
                    additional_data = self.load_json_data(json_file_path)
                    data.update(additional_data)  # Merge the JSON data
                except Exception as e:
                    print(f"Error loading JSON data: {e}")

            print(data)
            return  # Successfully completed

        print("All retries exhausted. Exiting.")

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    bot = RailwaysPNRBot()
    start_time = time.time()
    json_file_path = os.path.join(bot.curr_dir, 'legends.json')  # Specify your JSON file path
    try:
        bot.run('1234567890', json_file_path=json_file_path)
        print(f"Execution time: {time.time() - start_time} seconds")
    finally:
        bot.close()
