
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NEXUS_API_KEY"),
    base_url=os.getenv("NEXUS_BASE_URL")
)

try:
    response = client.chat.completions.create(
        model="nova-micro",
        messages=[
            {
                "role": "user",
                "content": "Explain what an AI agent is in two sentences."
            }
        ]
    )

    print("Nexus API connection successful!")
    print("\nModel Response:")
    print(response.choices[0].message.content)

except Exception as error:
    print("API Error:", error)
