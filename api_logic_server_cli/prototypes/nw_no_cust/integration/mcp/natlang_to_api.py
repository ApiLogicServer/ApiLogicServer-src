import openai
import requests
import json
import os

# Set your OpenAI API key here or via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-proj-..."

# The base ngrok URL of your live JSON:API server
NGROK_BASE_URL = "https://mcp_url.ngrok-free.app"

def ask_gpt_for_tool_context(natural_language_goal):
    prompt = f"""
You are an API planning assistant.

You receive a natural language goal and must generate a JSON tool_context for an API call.

The API follows JSON:API 1.1 and lives at: {NGROK_BASE_URL}/api  
Available resources: Customer, Order, Product

Goal: "{natural_language_goal}"

Respond ONLY with JSON in the following format:
{{
  "method": "GET",
  "url": "<full URL>",
  "query_params": {{ ... }},
  "headers": {{
    "Accept": "application/vnd.api+json"
  }},
  "expected_output": "Brief description of expected result"
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # Extract tool_context JSON block from the assistant message
    message = response["choices"][0]["message"]["content"]
    try:
        tool_context = json.loads(message)
        return tool_context
    except json.JSONDecodeError:
        print("Failed to parse GPT response as JSON:")
        print(message)
        return None

def execute_tool_context(tool_context):
    try:
        response = requests.get(
            tool_context["url"],
            headers=tool_context["headers"],
            params=tool_context["query_params"],
            timeout=10
        )
        print(f"✅ Response ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("Enter your natural language goal (e.g., 'List 3 customers from Germany'):")
    goal = input("> ")

    tc = ask_gpt_for_tool_context(goal)
    if tc:
        print("GPT tool_context:")
        print(json.dumps(tc, indent=2))
        print("Executing API call...")
        execute_tool_context(tc)
