import os
from urllib import response

from dotenv import load_dotenv
from openai import OpenAI

# ḷoad environment variables from .env file
load_dotenv()
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
# create client
client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url=os.getenv("GEMINI_API_BASE_URL"))

def main():
    question = input("Ask something: ")

    response = client.chat.completions.create(
        model = "gemini-3.5-flash",
        messages=[{
            "role": "user",
            "content": question
        }]
    )

    print("AI: ", response.choices[0].message.content)

if __name__ == "__main__":
    main()