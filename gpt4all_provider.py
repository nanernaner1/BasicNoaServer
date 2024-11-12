import requests
from provider_base import ProviderBase

class GPT4AllProvider(ProviderBase):
    def send_request(self, chat_messages, temperature):
        url = "http://localhost:4891/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": chat_messages,
            "temperature": temperature
        }
        
        try:
            # Debugging: Print the payload and headers
            print("Payload:", payload)
            print("Headers:", headers)
            
            print("Sending request to GPT4All")
            response = requests.post(url, headers=headers, json=payload, timeout=30)  # Increase timeout to 30 seconds
            response.raise_for_status()
            completion = response.json()
            
            # Debugging: Print the entire response
            print("Received response from GPT4All")
            
            if 'choices' in completion and len(completion['choices']) > 0:
                print("Choices:", completion['choices'][0])
                print("Message:", completion['choices'][0]['message'])
                print("Content:", completion['choices'][0]['message']['content'])
                return completion['choices'][0]['message']['content']
            else:
                print("Unexpected response format:", completion)
                return "Unexpected response format from GPT4All"
        
        except requests.exceptions.Timeout:
            print("Request to GPT4All timed out")
            return "Request to GPT4All timed out"
        except requests.exceptions.RequestException as e:
            print("Error while getting completion from GPT4All:", e)
            return "Failed to get response from GPT4All"
        except KeyError as e:
            print("Unexpected response format:", e)
            return "Unexpected response format from GPT4All"