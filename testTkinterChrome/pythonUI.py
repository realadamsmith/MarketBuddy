import tkinter as tk
import subprocess
from selenium import webdriver
import os
import sys

def my_function():
    print("Button clicked!")

root = tk.Tk()
root.geometry("800x600")  # Set the window size to 800x600 pixels

def get_chrome_driver_path():
    current_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0])
    return os.path.join(current_path, 'drivers', 'chromedriver.exe' if os.name == 'nt' else 'chromedriver')

def open_chrome():
    # Replace the path below with the path to your Chrome executable
    chrome_path = "C:\Program Files (x86)\chromedriver.exe"
    subprocess.Popen(chrome_path)

def open_chrome_with_selenium():
    global driver
    driver = webdriver.Chrome(executable_path='chromedriver.exe')  # Replace 'chromedriver.exe' with the path to your Chromedriver
    driver.get('https://www.google.com')
    
label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

button = tk.Button(root, text="Click me!", command=my_function)
button.pack()
button = tk.Button(root, text="Open Chrome with Selenium", command=open_chrome_with_selenium)
button.pack()

root.mainloop()
