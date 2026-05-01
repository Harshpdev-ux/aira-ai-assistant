from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values


env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")  
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Missing GroqAPIKey in .env file")

client = Groq(api_key=GroqAPIKey)


System = f"""Hello, I am {Username}. You are an AI chatbot named {Assistantname} with real-time web access.
- Provide answers in a professional way with proper grammar.
- Just answer the question concisely and professionally.
"""


chat_log_path = r"Data\ChatLog.json"
try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)


def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        answer = f"Search results for '{query}':\n[start]\n"
        for result in results:
            answer += f"Title: {result.title}\nDescription: {result.description}\n\n"
        return answer + "[End]"
    except Exception as e:
        return f"Error fetching Google Search results: {str(e)}"


def AnswerModifier(answer):
    return "\n".join(line for line in answer.split("\n") if line.strip())


def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}."


def RealtimeSearchEngine(prompt):
    global messages
    
   
    messages.append({"role": "user", "content": prompt})

    
    search_results = GoogleSearch(prompt)

    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": System},
                {"role": "system", "content": RealtimeInformation()},
                {"role": "user", "content": search_results},
            ] + messages,
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

        answer = answer.strip().replace("</s>", "")

        
        messages.append({"role": "assistant", "content": answer})

       
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        return f"Error generating response: {str(e)}"


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        print(RealtimeSearchEngine(user_input))
