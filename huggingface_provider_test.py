from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# Convert this simple application into a Python API server running on FastAPI in Object Oriented Programming.
# Include adapters for communicating with HuggingFace API as depicted in the code below, and communicate with Ollama Server
# Include feature for speech-to-text for input, that is then converted to a proper API POST request to HuggingFace_Hub



load_dotenv()

API_KEY=os.environ.get("API_KEY")

client = InferenceClient(api_key=API_KEY)

messages = [
	{ "role": "user", "content": "Tell me a story about a brown bear that lives in a forest with llamas" }
]

stream = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", 
	messages=messages, 
	temperature=0.5,
	max_tokens=2048,
	top_p=0.7,
	stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content)