import openai
import os
import json
from typing import List, Dict
from pydantic import BaseModel
from openai import OpenAI


client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))

class Table(BaseModel):
    columns: List[str]
    data_types: List[str]
    description: str
    
class DatabaseSchema(BaseModel):
    tables: list[Table]

def gen_datamodel():
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a data modeling expert, you design a database schema."},
            {"role": "user", "content": "Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, to for a project management system. The system should store information about projects, tasks, users, and comments."},
        ],
        # response_format=DatabaseSchema,
    )
    
    data = completion.choices[0].message.content
    print(json.dumps(json.loads(data), indent=4))
    pass
    
    
gen_datamodel()
