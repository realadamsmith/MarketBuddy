from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()  # Or use whatever browser you're working with
driver.get('https://www.google.com')  # Navigate to Google

search_box = driver.find_element(By.NAME, "q")  # Find the search box
search_box.send_keys("Hey")  # Enter your search query
search_box.send_keys(Keys.RETURN)  # Submit the search

time.sleep(2)  # Wait for the page to load

elements = driver.find_elements(By.XPATH, "//*[self::a or self::button]")  # Find the elements you're interested in.

for element in elements:
    try:
        print(f"Trying to click on element with text: '{element.text}'")
        element.click()
        time.sleep(1)  # wait for the next page to load
        driver.back()  # go back to the previous page
        time.sleep(2)  # wait for the page to load
    except Exception as e:
        print(f"Failed to click on element with text: '{element.text}'. Error: {str(e)}")
