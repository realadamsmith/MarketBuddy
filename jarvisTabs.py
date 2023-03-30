from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
import threading
from queue import Queue

PATH = "C:\Program Files (x86)\chromedriver.exe"
width = 1200
height = 1200
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--window-size={width},{height}")


def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...", r.energy_threshold)
        r.adjust_for_ambient_noise(source, duration=1)

        print("Listening for command... (speak now)")
        audio = r.listen(source, phrase_time_limit=10, timeout=10)
        print("Processing your command...")

    try:
        command = r.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def google_search(query):
    driver.switch_to.window(driver.window_handles[-1])
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    print(f"Searching for '{query}' on Google")

def click_news_tab():
    # Switch to the last opened tab
    driver.switch_to.window(driver.window_handles[-1])

    # Find the "News" tab and click on it
    try:
        news_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "&tbm=nws")]'))
        )
        news_tab.click()
        print("Switching to 'News' tab")
    except TimeoutException:
        print("Couldn't find 'News' tab")    
    except ElementNotInteractableException as e:
        print("Element not interactable, can't click on the news tab:", e)


driver = webdriver.Chrome(options=chrome_options)
search_variations = ["search for", "google", "find", "look up", "lookup", "search"]
open_tab_variations = ["open tab", "open new tab", "open a tab", "new tab"]

while True:
    command = listen_for_command()

    if command is not None:
        command = command.lower()

        if any(variation in command for variation in open_tab_variations):
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            print("Opening a new tab")

        elif "close tab" in command:
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            print("Current tab closed")


        elif "go to" in command:
            domain = command.replace("go to", "").strip()
            
            if not domain.startswith("http"):
                domain = f"https://{domain}"
            
            if "." not in domain:
                domain += ".com"
            
            try:
                # Set a timeout for loading the page
                timeout = 3
                driver.set_page_load_timeout(timeout)
                
                driver.get(domain)
                print(f"Navigating to {domain}")
                
            except WebDriverException as e:
                print(f"Could not navigate to {domain} due to an error: {e}")

        elif "news" in command.lower():
            click_news_tab()


        if any(variation in command for variation in search_variations):
            for variation in search_variations:
                if variation in command:
                    query = command.replace(variation, "").strip()
                    break
            
            google_search(query)
                    

        elif "quit" in command or "exit" in command:
            driver.quit()
            print("WebDriver closed")
            break


# CONCURRENCY IN THE SPEECH WE NEED
# Grab clickable elements on the page and display them
# Make the voice recognition faster.