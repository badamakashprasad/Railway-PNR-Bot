# Railways PNR Bot

## Overview

RailwaysPNRBot is a Python automation script that uses Selenium and Tesseract OCR to retrieve PNR (Passenger Name Record) status from the Indian Railways website. The bot handles dynamic web elements and CAPTCHAs, making it a useful tool for automated inquiries.

## Features

- **Automated Web Interaction**: Interacts with the Indian Railways PNR inquiry page.
- **CAPTCHA Solving**: Utilizes Tesseract OCR to solve CAPTCHAs.
- **Dynamic Waiting**: Implements explicit waits for page elements to ensure reliability.
- **JSON Data Integration**: Merges additional data from a JSON file with retrieved data.

## Requirements

- Python 3.x
- Selenium
- Tesseract OCR
- Pillow
- Pandas

## Installation

1. **Install Python**: Ensure you have Python 3.x installed.
2. **Install Dependencies**: Use pip to install the required packages:

   ```bash
   pip install -r requirements.txt
3. **Download Tesseract OCR**: Install Tesseract OCR from Tesseract at UB Mannheim.
Note the installation path (e.g., C:\\Program Files\\Tesseract-OCR\\tesseract.exe).
4. **Download ChromeDriver**: Download the ChromeDriver from ChromeDriver downloads.
Ensure the version matches your installed Chrome version.
Place the chromedriver.exe in the same directory as this script.

## Usage

1. **Configure the Script**: Set the path to your chromedriver.exe and Tesseract executable in the RailwaysPNRBot class.
Specify the JSON file path if additional data is needed.
2. **Run the Bot**: You can run the bot by executing the script:
   ```bash
   python railways_pnr_bot.py
Replace '1234567890' in the run method call with the desired PNR number.

## Troubleshooting

1. **CAPTCHA Fails**: If the bot fails to solve the CAPTCHA after multiple attempts, ensure that Tesseract is correctly installed and accessible.
2. **Element Not Found**: Increase the wait times if elements take longer to load on the webpage.

## License
- This project is open source and available under the MIT License.
