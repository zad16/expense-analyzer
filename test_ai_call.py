from app import get_system_prompt, TOOLS
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

messages = [
    {"role": "system", "content": get_system_prompt()},
    {"role": "user", "content": "how much did i spend on \"rice\" last month?"}
]

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

ai_msg = response.choices[0].message
print("Tool calls:")
if ai_msg.tool_calls:
    for tc in ai_msg.tool_calls:
        print(f"Name: {tc.function.name}")
        print(f"Args: {tc.function.arguments}")
        args = json.loads(tc.function.arguments)
        search_term = args.get("search_term")
        print(f"Extracted search_term: {repr(search_term)}")
else:
    print("No tool calls.")
