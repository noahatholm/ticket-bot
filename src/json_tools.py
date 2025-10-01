import json



def load_json(path_to_json):
    default = {
        "model":"meta-llama/Llama-3.2-3B-Instruct",
        "log_channel": "1422698365577068586",
        "prefix": "!",
        "ticket_category": None
    }
    try:
        with open(path_to_json, "r") as f:
            data = json.load(f)
            return data     
    except Exception as e:
        print("Json File Not Found Creating One With Default Values")
        with open(path_to_json, 'w') as f:
            json.dump(default,f,indent=4)
            print("New Json File created")
        return default
    

def get_default():
    return{
        "channel_id": None,
        "message_id": None,
        "message_header": "Support Tickets",
        "message_content": "To create a ticket react with 📩",
        "message_button": "Click Me!"
    }

def save_button(path_to_save,button_data):

    try:
        with open(path_to_save,"r") as f:
            json.dump(button_data,f,indent=4)
        return True
    except:
        print("Unable to save Json creating Default")
        with open(path_to_save,"w") as f:
            json.dump(get_default(),f,indent=4)
        return False



def load_button(path_to_button):
    try:
        with open(path_to_button,"r") as f:
            return json.load(f)
    except Exception as e:
        print (f"Unable to Open File {e}")
        return get_default()