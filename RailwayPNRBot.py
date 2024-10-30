import time
import json
import os

from OCRToText import OCRToText
from WebScrapper import WebScrapper
from constants import PNR_URL,INPUT_PNR_NO_ID,PNR_SUBMIT_ID,INPUT_CAPTCHA_ID,CAPTCHA_IMAGE_ID,CAPTCHA_SUBMIT_ID,JOURNEY_DETAILS_ID,CURRENT_STATUS_ID,OTHER_DETAILS_ID,LEGEND_FILE_NAME


class RailwaysPNRBot:
    def __init__(self):
        self.CURR_DIR = os.path.dirname(os.path.abspath(__file__))
        self.webScrapper = WebScrapper(self.CURR_DIR)
        self.CaptchaSolver = OCRToText()
        self.legend_file_path = os.path.join(self.CURR_DIR,LEGEND_FILE_NAME)
        

    def load_json_data(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def get_legend_json_data(self,path):
        if path:
            try:
                legend_data = self.load_json_data(path)
                return legend_data
            except Exception as e:
                print(f"Error loading JSON data: {e}")

    def run(self, pnr, max_retries=3):
        for attempt in range(max_retries):
            self.webScrapper.getDriver(PNR_URL)

            # Input PNR number
            self.webScrapper.getElementByID(INPUT_PNR_NO_ID).send_keys(pnr)
            self.webScrapper.getElementByID(PNR_SUBMIT_ID).click()

            # Wait for CAPTCHA image to be present and solve it
            CAPTCHA_element = self.webScrapper.getWaitElementByID(CAPTCHA_IMAGE_ID)
            CAPTCHA_image = self.webScrapper.capture_image_element(CAPTCHA_element)
            CAPTCHA_answer = self.CaptchaSolver.solve_captcha(CAPTCHA_image)
            
            # Submit CAPTCHA answer
            self.webScrapper.getElementByID(INPUT_CAPTCHA_ID).send_keys(CAPTCHA_answer)
            self.webScrapper.getElementByID(CAPTCHA_SUBMIT_ID).click()

            # Wait for journey details table
            try:
                journey_details_info_table = self.webScrapper.wait_for_table(JOURNEY_DETAILS_ID)
                ticket_status_info_table = self.webScrapper.wait_for_table(CURRENT_STATUS_ID)
                other_details_table = self.webScrapper.wait_for_table(OTHER_DETAILS_ID)
            except ValueError as e:
                print(e)
                print("Retrying the entire process...")
                continue  # Retry the whole process

            # If all is successful, extract data
            data = {
                'journeyDetailsInfo': self.webScrapper.get_dict_from_web_page_table(journey_details_info_table)[0],
                'ticketStatusInfo': self.webScrapper.get_dict_from_web_page_table(ticket_status_info_table),
                'otherDetails': self.webScrapper.get_dict_from_web_page_table(other_details_table)[0]
            }

            # Load additional JSON data if provided
            additional_data = self.get_legend_json_data(LEGEND_FILE_NAME)
            data.update(additional_data)  # Merge the JSON data

            print(data)
            return  # Successfully completed
        
        print("All retries exhausted. Exiting.")



if __name__ == "__main__":
    bot = RailwaysPNRBot()
    start_time = time.time()
    bot.run(pnr = '2919748626')
    print(f"Execution time: {time.time() - start_time} seconds")
    
