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
from selenium.common.exceptions import JavascriptException
import tkinter as tk
import numpy as np
import soundfile as sf
import os 
import pyaudio
import wave

PATH = "C:\Program Files (x86)\chromedriver.exe"
width = 1200
height = 1200
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--window-size={width},{height}")
root = tk.Tk()

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            for char in "Listening..":
                time.sleep(0.02)
                print(char, end='', flush=True)
            audio = r.listen(source, phrase_time_limit=5, timeout=10)
            print(" Processing..")
        except sr.WaitTimeoutError:
            print("Listening timed out, try again.")
            return None
    try:
        command = r.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand")
        return None
    
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None
    


def get_clickable_elements(max_elements=75):
    print("Checking elements")
    clickable_elements = driver.find_elements(By.XPATH, "//*[self::a or self::button]")
    clickable_elements = clickable_elements[:max_elements]
    element_dict = {}
    for index, element in enumerate(clickable_elements, start=1):
        element_text = element.text.strip()
        if not element_text or "accessibility" in element_text.lower():
            continue
        first_two_words = " ".join(element_text.split()[:2])
        if first_two_words:
            element_dict[first_two_words.lower()] = element
            create_custom_tooltip(element, element_text)
            print(f"{index}. {first_two_words}")
    return element_dict        

def update_clickable_elements():
    WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//*[self::a or self::button]")))
    global element_dict
    element_dict = get_clickable_elements()

def has_clickable_elements(driver):
    elements = driver.find_elements(By.XPATH, "//*[self::a or self::button]")
    return len(elements) > 0

def create_custom_tooltip(element, tooltip_text):
    tooltip_words = tooltip_text.split()
    truncated_tooltip_text = ' '.join(tooltip_words[:2])
    script = """
    var element = arguments[0];
    var tooltip = document.createElement("div");
    tooltip.style.position = "absolute";
    tooltip.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    tooltip.style.color = "white";
    tooltip.style.padding = "5px";
    tooltip.style.borderRadius = "5px";
    tooltip.style.fontSize = "14px";
    tooltip.style.zIndex = "9999";
    tooltip.innerHTML = arguments[1];
    tooltip.id = "custom_tooltip";
    document.body.appendChild(tooltip);

    function update_tooltip_position() {{
        var rect = element.getBoundingClientRect();
        tooltip.style.top = (rect.top + window.pageYOffset - tooltip.offsetHeight - 5) + "px";
        tooltip.style.left = (rect.left + window.pageXOffset + rect.width / 2 - tooltip.offsetWidth / 2) + "px";
    }}
    
    update_tooltip_position();
    window.addEventListener("scroll", update_tooltip_position);
    """
    tooltip_text = tooltip_text.replace('"', '&quot;').replace("'", "&#39;")
    if tooltip_text:
        try:
            driver.execute_script(script, element, truncated_tooltip_text)

        except JavascriptException:
            print(f"Error creating tooltip for element: {tooltip_text}")

def google_search(query):
    driver.switch_to.window(driver.window_handles[-1])
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    print(f"Searching for '{query}' on Google")

def record_system_audio(duration):
    # Record system audio
    chunk = 1024
    channels = 1
    rate = 44100
    sample_format = pyaudio.paInt16

    audio = pyaudio.PyAudio()
    stream = audio.open(format=sample_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    print("Starting recording...")
    frames = []
    start_time = time.time()

    while time.time() - start_time < duration:
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished")

    stream.stop_stream()
    stream.close()
    audio.terminate()
    output_folder = "C:/Users/caspi/Downloads/recorded_audio.wav"

    wave_file = wave.open(output_folder, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(audio.get_sample_size(sample_format))
    wave_file.setframerate(rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

    print(f"Recording saved to {output_folder}")

def is_youtube_video(driver):
    url = driver.current_url
    return "youtube.com" in url and "watch" in url

driver = webdriver.Chrome(options=chrome_options)
search_variations = ["search for", "google", "find", "look up", "lookup", "search"]
open_tab_variations = ["open tab", "open new tab", "open a tab", "new tab"]
click_phrases = ["click element", "click on", "click"]
scroll_down = ["go down", "scroll down", "down"]
scroll_up = ["go up", "scroll up", "up"]


while True:
    command = listen_for_command()
    if is_youtube_video(driver):
        print("We're on youtube")
        record_system_audio(10)

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

        if any(variation in command for variation in search_variations):
            for variation in search_variations:
                if variation in command:
                    query = command.replace(variation, "").strip()
                    break
            
            google_search(query)
            try:
                WebDriverWait(driver, 4).until(has_clickable_elements)
                element_dict = get_clickable_elements()
            except TimeoutException:
                print("No clickable elements found")

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

                try:
                    WebDriverWait(driver, 4).until(has_clickable_elements)
                    element_dict = get_clickable_elements()
                except TimeoutException:
                    print("No clickable elements found")                

            except WebDriverException as e:
                print(f"Could not navigate to {domain} due to an error: {e}")

        elif "list elements" in command: # Might remove
            element_dict = get_clickable_elements()
            
        if any(variation in command for variation in click_phrases):
            for phrase in click_phrases:
                if command.startswith(phrase):
                    first_two_words = command.replace(phrase, "").strip().lower()
                    if first_two_words in element_dict:
                        element = element_dict[first_two_words]
                    try:
                        element.click()
                        print(f"Clicked on element with text '{first_two_words}'")
                        update_clickable_elements()
                    except:
                        print(f"Couldn't click on element with text '{first_two_words}'")

        elif "quit" in command or "exit" in command:
            driver.quit()
            print("WebDriver closed")
            break
        
root.mainloop()
