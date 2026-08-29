import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

print("Python:", sys.version)
print("API key configured:", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI()
print("Environment is ready.")
