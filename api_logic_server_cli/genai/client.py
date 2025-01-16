import os
from openai import AzureOpenAI
from openai import OpenAI


def get_ai_client():
    api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

    if not api_key:
        raise Exception("APILOGICSERVER_CHATGPT_APIKEY environment variable not set")

    azure_endpoint = os.getenv("APILOGICSERVER_CHATGPT_AZURE_ENDPOINT")
    if azure_endpoint:
        api_version = os.getenv("APILOGICSERVER_CHATGPT_AZURE_API_VERSION", "2024-10-21")
        client = AzureOpenAI(
            azure_endpoint = azure_endpoint, 
            api_key=api_key,  
            api_version=api_version)
        print(f"Using Azure OpenAI, endpoint: {azure_endpoint}, version: {api_version}")
    else:
        client = OpenAI(api_key=api_key)
    
    return client

