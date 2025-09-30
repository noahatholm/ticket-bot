import json



def load_json(path_to_json):
    default = {
        "model":"meta-llama/Llama-3.2-3B-Instruct",
        "ticket_channel":"1422697916992065690",
        "ticket_message": None,
        "log_channel": "1422698365577068586",
        "prefix": "!",
        "ticket_message_header": "Support Tickets",
        "ticket_message_content":"To create a ticket react with 📩"
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