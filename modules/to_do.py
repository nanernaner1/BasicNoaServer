import os
import json
import datetime


class ToDoManager:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        self.to_do_list = self.load_to_do_list()
        self.module_name = "To-Do" # used to filter it in menus and such for later
        self.module_desc = "A module to manage to-do items." # used to describe the module in menus and such for later
        self.module_trigger_phrases = ["create to-do", "create todo", "create to do", "list to-dos", "list todos", "list to dos", "remind me", "list reminders", "reminder to", "remember to", "remember that"] # used to trigger the module in the main AI loop for later, don't need to describe them vs be descriptive in name? simple trigger that isn't as cool as wider trigger options but maybe more robust for now? 
        self.list_trigger_phrases = ["list", "what are", "what to", "what is there", "what do", "remind me", "what does"] #second pass, to find the relevant function to trigger off the input
        self.item_create_trigger_phrases = ["create", "add", "make", "remember", "reminder"] #second pass again, to find the relevant function to trigger off the input

    def load_to_do_list(self):
        to_do_list = []
        for filename in os.listdir(self.dir_path):
            if filename.endswith('.json'):
                with open(os.path.join(self.dir_path, filename), 'r') as file:
                    to_do_list.append(json.load(file))
        return to_do_list

    def save_to_do_item(self, item):
        timestamp = item["timestamp"].replace(":", "-")
        filename = f"{timestamp}.json"
        with open(os.path.join(self.dir_path, filename), 'w') as file:
            json.dump(item, file, default=str)

    def create_to_do(self, to_do_data):
        timestamp = datetime.datetime.now().isoformat()
        #remove the trigger phrases from the data
        for phrase in trigger_phrases:
            to_do_data = to_do_data.replace(phrase, "")
        to_do_data = to_do_data.strip()
        
        for phrase in self.list_trigger_phrases:
            to_do_data = to_do_data.replace(phrase, "")
            
        item = {"timestamp": timestamp, "data": to_do_data}
        
        self.to_do_list.append(item)
        self.save_to_do_item(item)

    def delete_to_do(self, index):
        if 0 <= index < len(self.to_do_list):
            del self.to_do_list[index]
            self.save_all_to_do_items()

    def save_all_to_do_items(self):
        for item in self.to_do_list:
            self.save_to_do_item(item)

    def find_to_do(self, query):
        relevant_items = [item for item in self.to_do_list if query in item["data"]]
        if not relevant_items:
            return ["No to-do items found for the specified date range."]
        return relevant_items

    def list_to_dos(self):
        #loop all items and return a string saying "To-Do item {index}: {data}"
        to_do_list = []
        for i, item in enumerate(self.to_do_list):
            to_do_list.append(f"To-Do item {i}: {item['data']}")
        return to_do_list
    
    #list to-dos for a date range
    def list_to_dos_for_date_range(self, start_time, end_time):
        relevant_items = [] #list of items that are relevant, but default none
        for item in self.to_do_list:
            item_timestamp = datetime.datetime.fromisoformat(item["timestamp"])
            if start_time <= item_timestamp <= end_time:
                relevant_items.append(item)
        if not relevant_items:
            return ["No to-do items found for the specified date range."]
        return relevant_items
    

data_dir = "data"
tm = ToDoManager(os.path.join(data_dir, "to_do"))

def ingest(data, provider):
    
    print("[To-Do Module] Ingesting data:", data)
    
    
    #first, check if there is any string with a trigger phrase, such as to-do, to do todo etc
    if any(phrase in data.lower() for phrase in trigger_phrases):
        print("[To-Do Module] Found a trigger phrase in request")
        
        if any(phrase in data.lower() for phrase in tm.list_trigger_phrases):
            if any(phrase in data.lower() for phrase in ["today", "now", "current"]):
                to_do_list = tm.list_to_dos_for_date_range(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), datetime.datetime.now())
                print("[To-Do Module] Listing all To-Do items for today:", to_do_list)
                return to_do_list
            elif any(phrase in data.lower() for phrase in ["yesterday"]):
                to_do_list = tm.list_to_dos_for_date_range(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1), datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
                print("[To-Do Module] Listing all To-Do items for yesterday:", to_do_list)
                return to_do_list
            elif any(phrase in data.lower() for phrase in ["tomorrow", "next"]):
                to_do_list = tm.list_to_dos_for_date_range(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1), datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
                print("[To-Do Module] Listing all To-Do items for tomorrow:", to_do_list)
                return to_do_list
            elif any(phrase in data.lower() for phrase in ["this week", "week"]):
                to_do_list = tm.list_to_dos_for_date_range(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=datetime.datetime.now().weekday()), datetime.datetime.now())
                print("[To-Do Module] Listing all To-Do items for this week:", to_do_list)
                return to_do_list
            elif any(phrase in data.lower() for phrase in ["this month", "month"]):
                to_do_list = tm.list_to_dos_for_date_range(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=datetime.datetime.now().day - 1), datetime.datetime.now())
                print("[To-Do Module] Listing all To-Do items for this month:", to_do_list)
                return to_do_list
            
            to_do_list = tm.list_to_dos()
            print("[To-Do Module] Listing all To-Do items as no filter was set for trigger phrase pickup, might be a specific query within all notes. could filter by date if too many eventually....?", to_do_list)
            return to_do_list
        if any(phrase in data.lower() for phrase in tm.item_create_trigger_phrases):
            tm.create_to_do(data)
            print("[To-Do Module] To-Do created")
            return "To-Do created."

    return ""