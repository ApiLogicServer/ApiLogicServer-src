import os
from openai import AzureOpenAI
from openai import OpenAI

api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

azure_endpoint = os.getenv("APILOGICSERVER_CHATGPT_AZURE_ENDPOINT")
if azure_endpoint:
    api_version = os.getenv("APILOGICSERVER_CHATGPT_AZURE_API_VERSION", "2024-10-21")
    client = AzureOpenAI(
        azure_endpoint = azure_endpoint, 
        api_key=api_key,  
        api_version=api_version)
else:
    client = OpenAI(api_key=api_key)






