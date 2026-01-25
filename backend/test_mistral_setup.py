import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

def test_mistral_autonomy():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY not found in backend/.env")
        return

    client = Mistral(api_key=api_key)
    print("✅ Mistral client initialized successfully.")
    
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        print(f"✅ Mistral Communication: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Mistral Communication failed: {e}")

if __name__ == "__main__":
    test_mistral_autonomy()
