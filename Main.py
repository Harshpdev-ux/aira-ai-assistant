import asyncio
import threading
import subprocess
import json
import os
from time import sleep

from Frontend.GUI import (
    GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen,
    TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, QueryModifier,
    GetMicrophoneStatus, GetAssistantStatus)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from Backend.Automation import Control_Light


env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistant", "Assistant")


DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""


Functions = {"open", "close", "play", "system", "content", "google search", "youtube search", "control light"}


def show_default_chat_if_no_chats():
    """Ensure chat history is initialized if empty."""
    chat_log_path = 'Data/Chatlog.json'
    
    with open(chat_log_path, "r", encoding='utf-8') as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
                f.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
                f.write(DefaultMessage)

def read_chat_log_json():
    """Read and return chat log data as JSON."""
    with open('Data/Chatlog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def integrate_chat_log():
    """Convert chat log into formatted text and store it."""
    json_data = read_chat_log_json()
    formatted_chatlog = "\n".join(
        f"{Username if entry['role'] == 'user' else Assistantname}: {entry['content']}"
        for entry in json_data
    )
    
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def show_chats_on_gui():
    """Update GUI chat window."""
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        data = file.read()
    
    if data:
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(data)

def initialize_execution():
    """Prepare the assistant before activation."""
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    show_default_chat_if_no_chats()
    integrate_chat_log()
    show_chats_on_gui()

initialize_execution()

def process_decision(query):
    """Analyze the query and take action accordingly."""
    SetAssistantStatus("Thinking...")
    decisions = FirstLayerDMM(query)
    print(f"\nDecision: {decisions}\n")

    merged_query = " and ".join(
        [" ".join(d.split()[1:]) for d in decisions if d.startswith(("general", "realtime"))]
    )

    
    if any("light on" in decision for decision in decisions):
        Control_Light("on")  
        SetAssistantStatus("Light is ON.")
        ShowTextToScreen(f"{Assistantname}: Light is now ON.")
        TextToSpeech("Light is now ON.")
        return

    if any("light off" in decision for decision in decisions):
        Control_Light("off")  
        SetAssistantStatus("Light is OFF.")
        ShowTextToScreen(f"{Assistantname}: Light is now OFF.")
        TextToSpeech("Light is now OFF.")
        return



    image_generation_query = next((q for q in decisions if "generate" in q), None)

    if image_generation_query:
        with open(r"Frontend/Files/ImageGeneration.data", "w") as file:
            file.write(f"{image_generation_query},True")

        threading.Thread(
            target=lambda: subprocess.run(['python', r'Backend/ImageGeneration.py']),
            daemon=True
        ).start()

   
    if any(d.startswith(func) for func in Functions for d in decisions):
        asyncio.run(Automation(list(decisions)))

   
    if any(d.startswith("realtime") for d in decisions):
        SetAssistantStatus("Searching...")
        answer = RealtimeSearchEngine(QueryModifier(merged_query))
        ShowTextToScreen(f"{Assistantname}: {answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(answer)
        return

   
    for q in decisions:
        if "general" in q:
            SetAssistantStatus("Thinking...")
            answer = ChatBot(QueryModifier(q.replace("general", "").strip()))
            ShowTextToScreen(f"{Assistantname}: {answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(answer)
            return

        elif "exit" in q:
            answer = ChatBot(QueryModifier("Okay, Bye!"))
            ShowTextToScreen(f"{Assistantname}: {answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(answer)
            os._exit(1)

def main_execution():
    """Primary execution loop for handling user queries."""
    SetAssistantStatus("Listening...")
    query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {query}")
    
    process_decision(query)

def first_thread():
    """Monitor microphone status and trigger assistant processing."""
    while True:
        if GetMicrophoneStatus() == "True":
            main_execution()
        elif GetAssistantStatus() != "Available...":
            SetAssistantStatus("Available...")
        sleep(0.1)

def second_thread():
    """Run the GUI."""
    GraphicalUserInterface()

if __name__ == "__main__":
    threading.Thread(target=first_thread, daemon=True).start()
    second_thread()
