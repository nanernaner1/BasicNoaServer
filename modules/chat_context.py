import os
import json

class ChatContextManager:
    def __init__(self, dir_path, max_length=50):
        self.dir_path = dir_path
        self.max_length = max_length
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        self.context_list = self.load_context_list()
        self.module_name = "Chat Context" # used to filter it in menus and such for later
        self.module_desc = "A module to manage chat context." # used to describe the module in menus and such for later
        self.trigger_phrases = ["context module", "chat manager module"] # used to trigger the module in the main AI loop for later, don't need to describe them vs be descriptive in name? simple trigger that isn't as cool as wider trigger options but maybe more robust for now?
        self.wipe_context_trigger_phrases = ["wipe context", "clear context", "forget context", "wipe", "erase", "reset"] #second pass, to find the relevant function to trigger off the input

    def load_context_list(self):
        context_list = []
        context_file = os.path.join(self.dir_path, "context.json")
        if os.path.exists(context_file):
            with open(context_file, 'r') as file:
                context_list = json.load(file)
        return context_list
    
    def wipe_context_list(self):
        self.context_list = []
        self.save_context_list()
        

    def save_context_list(self):
        context_file = os.path.join(self.dir_path, "context.json")
        with open(context_file, 'w') as file:
            json.dump(self.context_list, file)

    def add_context(self, context_data):
        context_data = context_data.strip()
        
        if len(self.context_list) >= self.max_length:
            self.context_list.pop(0)  # remove the oldest context
        self.context_list.append(context_data)
        self.save_context_list()

    def list_contexts(self):
        return self.context_list
    
    def ingestAndAbstract(data, provider):
        print("[Chat Context Module] Ingesting data:", data)
        cm = ChatContextManager(os.path.join(data_dir, "chat_context"))
    
        # Add the new data to the context
        cm.add_context(data)
        print("[Chat Context Module] Context added")
    
        # List all context items
        context_list = cm.list_contexts()
        print("[Chat Context Module] Listing all context items:", context_list)
        return context_list

data_dir = "data"
cm = ChatContextManager(os.path.join(data_dir, "chat_context")) #single instance
def ingest(data, provider):
    #context = ChatContextManager(os.path.join(data_dir, "chat_context"))
    print("[Chat Context Module] Ingesting data:", data)
    
    if any(phrase in data for phrase in cm.trigger_phrases):
        print("[Chat Context Module] Trigger phrase detected")
        if any(phrase in data for phrase in cm.wipe_context_trigger_phrases):
            print("[Chat Context Module] wipe trigger phrase detected")
            cm.wipe_context_list()
            print("[Chat Context Module] Context wiped")
    
    # Add the new data to the context
    cm.add_context(data)
    print("[Chat Context Module] Context added")
    
    # List all context items
    context_list = cm.list_contexts()
    print("[Chat Context Module] Listing all context items:", context_list)
    return context_list