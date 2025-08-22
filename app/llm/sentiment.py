from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()
response = client.responses.create(
    model = OPENAI_MODEL,
    reasoning = {"effort": "medium"},
    input = [
        {"role" : "system", "content" : }
    ]