# provider_base.py
from abc import ABC, abstractmethod

class ProviderBase(ABC):
    @abstractmethod
    def send_request(self, chat_messages, temperature):
        pass