from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import serial
import time


env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTK00 SY7ric", "ZOLCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
           "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTK00", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
           "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfke", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Assistant')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]


def Control_Light(state):
    try:
        # Open serial connection
        arduino = serial.Serial('COM7', 9600, timeout=1)  # Adjust the COM port if needed
        time.sleep(2)  # Allow time for the Arduino to initialize

        # Print debug information about the connection
        print(f"Connected to Arduino on {arduino.portstr}")

        if state.lower() == "on":
            arduino.write(b'1')  # Send '1' to turn on the light
            time.sleep(1)  # Wait for the Arduino to process the command
            response = arduino.readline().decode().strip()  # Read Arduino's response
            arduino.close()
            print(f"Arduino response: {response}")
            return "Light turned ON" if not response else response
        
        elif state.lower() == "off":
            arduino.write(b'0')  # Send '0' to turn off the light
            time.sleep(1)  # Wait for the Arduino to process the command
            response = arduino.readline().decode().strip()  # Read Arduino's response
            arduino.close()
            print(f"Arduino response: {response}")
            return "Light turned OFF" if not response else response
        
        else:
            return "Invalid command. Use 'on' or 'off'."
    
    except serial.SerialException as e:
        return f"Error: Could not connect to Arduino. {e}"


def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})  # Add user prompt
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("content ", "")
    contentByAI = ContentWriterAI(Topic)

    os.makedirs("Data", exist_ok=True)  # Ensure the directory exists

    file_path = rf"Data\{Topic.lower().replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(contentByAI)

    OpenNotepad(file_path)
    return True

def YoutubeSearch(Topic):
    UrlSearch = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(UrlSearch)
    return True


def playYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": user_agent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            link = extract_links(html)[0]
            webopen(link)

        return True


def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume up")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    actions = {
        "mute": mute,
        "unmute": unmute,
        "volume up": volume_up,
        "volume down": volume_down,
    }

    if command in actions:
        result = actions[command]()
        print(result)  # Print the action result
        return True
    else:
        print(f"Unknown system command: {command}")
        return False
    


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:

        if command.startswith("open"):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open").strip())
            funcs.append(fun)
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close").strip())
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(playYoutube, command.removeprefix("play ").strip())
            funcs.append(fun)
        elif command.startswith("content"):
            fun = asyncio.to_thread(Content, command.removeprefix("content").strip())
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search ").strip())
            funcs.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ").strip())
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system").strip())
            funcs.append(fun)
        elif command.startswith("control light "):
            fun = asyncio.to_thread(Control_Light, command.removeprefix("control light").strip())
            funcs.append(fun)
        elif command.startswith("control light "):
            fun = asyncio.to_thread(Control_Light, command.removeprefix("control light").strip())
            funcs.append(fun)
        elif "light on" in command:
            fun = asyncio.to_thread(Control_Light, "on")
            funcs.append(fun)
        elif "light off" in command:
            fun = asyncio.to_thread(Control_Light, "off")
            funcs.append(fun)
        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    asyncio.run(Automation(["light off"]))


