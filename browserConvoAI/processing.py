import speech_recognition as sr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


search_variants = ["search for", "google", "find", "look up", "lookup", "search"]
open_tab_variants = ["open tab", "open tap", "open table", "open new tab", "open a tab", "new tab"]
close_tab_variants = ["close tab", "close window", "close"]
go_to_variants = ["go to", "open"]
click_phrases = ["click element", "click on", "click", "quick"]
scroll_down = ["go down", "scroll down", "down"]
scroll_up = ["go up", "scroll up", "up"]


element_dict = {}

def process_command(command_q, driver, perform_command, element_dict, get_clickable_elements, update_clickable_elements ):
    while True:
        try:
            command = command_q.get()
            if command is None:
                print("No command received")
                continue
            command = command.lower()  
            if command == 'exit':  # Exit command to break the loop
                command_q.put(None)
                break
            print("We got here")
            if any(variation in command for variation in open_tab_variants):
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                print("Opening a new tab")
            elif any(variation in command for variation in close_tab_variants):
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                print("Current tab closed")


            elif any(variation in command for variation in search_variants):
                for variation in search_variants:
                    if variation in command:
                        query = command.replace(variation, "").strip()
                        break
                perform_command("search", query)

            elif any(variation in command for variation in go_to_variants):
                domain = command.replace("go to", "").strip()
                if not domain.startswith("http"):
                    domain = f"https://{domain}"
                if "." not in domain:
                    domain += ".com"
                perform_command("go_to", domain)
                
            elif any(variation in command for variation in click_phrases):
                first_two_words = None
                for phrase in click_phrases:
                    if command.startswith(phrase):
                        first_two_words = " ".join(command.replace(phrase, "").split()[:2]).strip().lower()

                if first_two_words and first_two_words in element_dict:
                    element = element_dict[first_two_words]
                    try:
                        element.click()
                        print(f"Clicked on element with text '{first_two_words}'")
                        update_clickable_elements()
                    except Exception as e:
                        print(f"Couldn't click on element with text '{first_two_words}'. Error: {str(e)}")
                else:
                    print(f"No element found with text '{first_two_words if first_two_words else 'unknown'}'")



        except Exception as e:
            print(f"Exception occurred in processing thread: {e}")