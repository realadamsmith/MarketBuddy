import speech_recognition as sr
import time

def raw_listen(raw_q):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                for char in "Listening..":
                    time.sleep(0.02)
                    print(char, end='', flush=True)
                audio = r.listen(source, phrase_time_limit=3)
                raw_q.put(audio)
            except sr.WaitTimeoutError:
                print("Listening timed out, try again.")
            except sr.UnknownValueError:
                print("Could not understand")

def listen(raw_q, command_q):
    r = sr.Recognizer()
    while True:
        audio = raw_q.get()
        if audio is None:  # Termination signal
            command_q.put(None)
            break
        try:
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            command_q.put(command)
        except sr.UnknownValueError:
            print("??")
