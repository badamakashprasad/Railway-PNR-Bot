import pytesseract
import re
import time

class OCRToText:
    def __init__(self):
        self.tesseract_executable = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_executable
    
    def get_captcha_answer(self, t):
        digits = [d for d in re.split(r"\D", t) if d]
        operand = re.findall(r"\D", t)[0]
        return int(digits[0]) + int(digits[1]) if operand == '+' else int(digits[0]) - int(digits[1])

    def solve_captcha(self, captcha_image, max_retries=3):
        captcha_image.show()
        for attempt in range(max_retries):
            captcha_text = pytesseract.image_to_string(captcha_image).strip()
            if captcha_text and re.search(r'\d', captcha_text):  # Check if digits are found
                return self.get_captcha_answer(captcha_text)
            print(f"Attempt {attempt + 1}: OCR failed. Retrying...")
            time.sleep(1)  # Optional: wait before retrying
        raise ValueError("Failed to solve CAPTCHA after multiple attempts.")
