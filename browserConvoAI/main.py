import speech_recognition as sr
from selenium import webdriver
import threading
from queue import Queue
import tkinter as tk
import numpy as np
import soundfile as sf
import os 
import pyaudio
import wave
import queue
from listen import listen, raw_listen
from processing import process_command
import time

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import JavascriptException

PATH = "C:\Program Files (x86)\chromedriver.exe"
width = 1000
height = 1200
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--window-size={width},{height}")
root = tk.Tk()

element_dict = {}


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
    print("Total elements found:", len(element_dict))
    print("Elements:", element_dict.keys())
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

        except JavascriptException as e:
            print(f"Error creating tooltip for element: {tooltip_text}. Error: {str(e)}")

def google_search(query):
    driver.switch_to.window(driver.window_handles[-1])
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    print(f"Searching for '{query}' on Google")
    try:
        WebDriverWait(driver, 4).until(has_clickable_elements)
        element_dict = get_clickable_elements()
    except TimeoutException:                    
        print("No clickable elements found")

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

def perform_command(command_type, *args):
    if command_type == 'search':
        query = args[0]
        google_search(query)
        print("Lets go")
    elif command_type == 'go_to':
        try:
            # Set a timeout for loading the page
            timeout = 3
            driver.set_page_load_timeout(timeout)
            driver.get(args[0])
            print(f"Navigating to {args[0]}")
            try:
                WebDriverWait(driver, 4).until(has_clickable_elements)
                element_dict = get_clickable_elements()
            except TimeoutException:
                print("No clickable elements found")                

        except WebDriverException as e:
            print(f"Could not navigate to {args[0]} due to an error: {e}")

    elif command_type == 'list_elements':
        get_clickable_elements()

    elif command_type == 'click_element':
        element_name = args[0]
        click_on_element(element_name)

    elif command_type == 'quit':
        driver.quit()
    else:
        print(f"Unknown command type: {command_type}")



driver = webdriver.Chrome(options=chrome_options)

raw_q = queue.Queue()  # This is a new queue for the raw audio data
command_q = queue.Queue()  # Renamed from 'q', this is now for the processed audio commands

raw_listen_thread = threading.Thread(target=raw_listen, args=(raw_q,))
listen_thread = threading.Thread(target=listen, args=(raw_q, command_q))
process_thread = threading.Thread(target=process_command, args=(command_q, driver, perform_command, element_dict, get_clickable_elements, update_clickable_elements))

# Start the threads
raw_listen_thread.start()
listen_thread.start()
process_thread.start()

# Wait for them to complete
raw_listen_thread.join()
raw_q.put(None)  # Signal to transcription thread that raw listening is done
listen_thread.join()
command_q.put(None)  # Signal to processing thread that transcription is done
process_thread.join()