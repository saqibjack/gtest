from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sys
import re


from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")  # Use 'new' for recent Chrome versions
options.add_argument("--no-sandbox")  # Needed for Docker
options.add_argument("--disable-dev-shm-usage")  # Avoid limited /dev/shm crash
options.add_argument("--disable-gpu")  # Often useful in headless mode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



from RecaptchaSolver import RecaptchaSolver




def get_user(email):
    return email.split('@')[0]

def extract_emails_from_file(filepath):
    email_list = []
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    try:
        with open(filepath, 'r') as file:
            for line in file:
                matches = email_pattern.findall(line)
                email_list.extend(matches)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

    return email_list


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_emails.py <Google_Form_URL> <filename>")
        sys.exit(1)
    gfrom_url = sys.argv[1]
    file_path = sys.argv[2]
    emails = extract_emails_from_file(file_path)

    #print("Extracted Emails:")
    for email in emails:
        #print(email)
        # Set up Selenium WebDriver (Make sure you have chromedriver installed)
        service = Service("/usr/local/bin/chromedriver")  # Change path to your chromedriver
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        # Open Google Form
        # form_url = "https://docs.google.com/forms/d/e/1FAIpQLScUCVMVrmlrLyQHJ4bF-Mk_tnZvco17N_BCI0p2g2y53CzaSQ/viewform"
        driver.get(gfrom_url)

        wait = WebDriverWait(driver, 10)

        time.sleep(2)  # Wait for the form to load

        # Fill in email
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
        email_field.send_keys(email)

        # Fill in text fields
        text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        if len(text_inputs) >= 2:
            text_inputs[0].send_keys(get_user(email))
            #amount random generation
            random_amount = round(random.uniform(361.99, 598.99), 2)
            text_inputs[1].send_keys(random_amount)

        time.sleep(1)

        # Select all radio buttons
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, '[role="radio"]')
        for radio in radio_buttons:
            try:
                driver.execute_script("arguments[0].click();", radio)
                time.sleep(1)
            except Exception as e:
                print(f"Could not click: {e}")

        # Click Submit button and solving captcha
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, '[role="button"]')
        for button in submit_buttons:
            if "Submit" in button.text:
                #print(f"Clicking button: {button.text}")
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(3)
                    iframe = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')

                    if iframe:
                        #print("reCAPTCHA detected. Attempting to solve...")
                        recaptchaSolver = RecaptchaSolver(driver)
                        recaptchaSolver.solveCaptcha()


                    break
                except Exception as e:
                    print(f"{email}")

        time.sleep(2)

        driver.quit()
