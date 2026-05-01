from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values


env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")  
Assistantname = env_vars.get("Assistant",)
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Missing GroqAPIKey in .env file")

client = Groq(api_key=GroqAPIKey)

chat_log_path = r"Data\ChatLog.json"

try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

System = f"""Hello, I am {Username}. You are a very accurate AI chatbot named {Assistantname} with real-time web access.
- Do not tell the time unless asked.
- Reply only in English.
- Keep answers concise and do not mention training data.
"""

SystemChatBot = [{"role": "system", "content": System}]


def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}."


def AnswerModifier(answer):
    return "\n".join(line for line in answer.split("\n") if line.strip())


def ChatBot(query):
    global messages  
    
    messages.append({"role": "user", "content": query})

    real_time_info = {"role": "system", "content": RealtimeInformation()}

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [real_time_info] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "").strip()

        messages.append({"role": "assistant", "content": answer})

        
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, something went wrong. Please try again."


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(ChatBot(user_input))
