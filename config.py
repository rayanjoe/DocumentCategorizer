from openai import AzureOpenAI

import os 
from dotenv import load_dotenv
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("api_key"),
    azure_endpoint=os.getenv("azure_endpoint"),
    api_version=os.getenv("api_version")
)