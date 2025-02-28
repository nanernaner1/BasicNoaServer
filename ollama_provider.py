import base64
import requests
from provider_base import ProviderBase

class OllamaProvider(ProviderBase):
    def send_request(self, chat_messages, temperature):
        url = "http://localhost:11434/api/chat"
        headers = {
            "Content-Type": "application/json",
            }
        payload = {
            "messages": chat_messages,
            "temperature": temperature,
            "model": "deepseek-r1:7b",
            # "model": "qwen2.5:3b",
            "stream": False
        }
        
        try:
            print("Sending request to Ollama")
            response = requests.post(url, headers=headers, json=payload, timeout=60)  # Increase timeout to 30 seconds
            response.raise_for_status()
            completion = response.json()
            
            # Debugging: Print the entire response
            print(f"Received response from {completion['model']}:", completion)
            print(f"Printing response keys: {completion.keys()}")
            
            if 'choices' in completion and len(completion['choices']) > 0:
                print("Choices:", completion['choices'][0])
                print("Message:", completion['choices'][0]['message'])
                print("Content:", completion['choices'][0]['message']['content'])
                return completion['choices'][0]['message']['content']
            elif 'message' in completion and len(completion['message']) > 0:
                print("Message:", completion['message'])
                print("Content:", completion['message']['content'])
                # message = completion['message']['content'].split("</think>")[1].strip()
                message = completion['message']['content'].split("</think>")[0].split("<think>")[1].strip()
                return message
            else:
                print("Unexpected response format:", completion)
                return "Unexpected response format from Ollama"
        
        except requests.exceptions.Timeout:
            print("Request to Ollama timed out")
            return "Request to Ollama timed out"
        except requests.exceptions.RequestException as e:
            print("Error while getting completion from Ollama:", e)
            return "Failed to get response from Ollama"
        except KeyError as e:
            print("Unexpected response format:", e)
            return "Unexpected response format from Ollama"

    def send_vision_request(self, base64_image_data, query):
        url = "http://localhost:11434/api/chat"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": "deepseek-r1:7b",
            "messages": [
                { 
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/png;base64,{base64_image_data}" }
                        }
                    ]
                }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }
        
        try:
            print("Sending image request to Vision Model")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Debugging: Print the entire response
            print("Received response from Vision Model:", result)
            
            if 'choices' in result and len(result['choices']) > 0:
                print("Choices:", result['choices'][0])
                print("Message:", result['choices'][0]['message'])
                print("Content:", result['choices'][0]['message']['content'])
                return result['choices'][0]['message']['content']
            else:
                print("Unexpected response format:", result)
                return "Unexpected response format from Vision Model"
        
        except requests.exceptions.Timeout:
            print("Request to Vision Model timed out")
            return "Request to Vision Model timed out"
        except requests.exceptions.RequestException as e:
            print("Error while getting response from Vision Model:", e)
            return "Failed to get response from Vision Model"
        except KeyError as e:
            print("Unexpected response format:", e)
            return "Unexpected response format from Vision Model"