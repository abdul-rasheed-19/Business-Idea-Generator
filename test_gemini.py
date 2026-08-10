from google import genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Check if API key exists
if not api_key:
    print("❌ GEMINI_API_KEY was not found.")
    exit()

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send a test request
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Give me one simple business idea for a college student."
)

print("\n🤖 Gemini Response:\n")
print(response.text)
