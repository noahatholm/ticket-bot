from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data import DataLoader
import json
import torch
import os

class myDataset(torch.utils.data.Dataset):
    def __init__(self,combined_data, tokenizer,device):
        self.length = len(combined_data)
        self.tokenizer = tokenizer
        self.device = device
        self.tokenized_data = self.__tokenize__(combined_data)
        

    def __tokenize__(self,data):
        return self.tokenizer(data,padding=True,truncation=True,return_tensors="pt").to(self.device)

    def __len__(self):
        return self.length
    
    def __getitem__(self, index):
        return {
            "input_ids": self.tokenized_data["input_ids"][index],
            "attention_mask": self.tokenized_data["attention_mask"][index],
            "labels": self.tokenized_data["input_ids"][index].clone() #We aren't using labelled data so just gonna give same for both
        }

#Takes a AutoModelForCausalLM object as well as the name of the finetuned model, the name also needs to have a name.json file in 
# finetuning that contains question answer examples for training
def finetune(model: AutoModelForCausalLM,tokenizer: AutoTokenizer,name: str, prompt: str ,*, epochs = 10, device = "cuda"):
    try:
        training_data = fetch_json_data(name)
    except:
        return False
    
    try:
        prompt = fetch_prompt(prompt)
    except:
        return False

    #print_json(training_data)

    lora_config = LoraConfig(
        task_type="CAUSAL_LM",
        r=64,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=['q_proj', 'v_proj']
        )
    
    #create lora model
    model = get_peft_model(model,lora_config)
    model.print_trainable_parameters()


    #We need to build our training data by adding the prompt to it as well as combining the answers to follow the question
    combined_training_data = combine_pairs(training_data,prompt)



    adam = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)

    #Create dataloader which will manage batches and shuffling them to prevent over fitting
    dataset = myDataset(combined_training_data,tokenizer,device)
    dataloader = DataLoader(dataset,batch_size=3,shuffle=True)


    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_index, batch in enumerate(dataloader):
            adam.zero_grad()
            #Forward pass to get model outputs and calculate loss
            output = model(**batch)
            loss = output.loss

            #backward pass
            loss.backward()
            adam.step()

            total_loss += loss.item()

        average_loss = total_loss / len(dataloader)
        print(f"Epoch: {epoch}, Average loss: {average_loss}")

    #Save new weights to disk
    os.makedirs("..//models/",exist_ok=True)
    model.save_pretrained("..//Models//"+name)
    return True




#Tokenizes an array of pairs ready for training
def combine_pairs(training_data,prompt):
    new_data = []
    answerTags = "\n<Answer>{}</Answer>"
    for data in training_data:
        question = data["question"]
        answer = data["answer"]
        new_data.append(prompt.format(question) + answerTags.format(answer))
    return new_data




def fetch_prompt(prompt_name):
    path_to_folder = "..//prompts/"
    try:
        with open(path_to_folder + prompt_name + ".txt") as f:
            prompt = f.read()
            return prompt
    except FileNotFoundError as e:
        print(f"File Not Found {e}")
        raise
    except Exception as e:
        raise

def fetch_json_data(name):
    path_to_folder = "..//finetuning/"
    try:
        with open(path_to_folder + name + ".json") as f:
            data = json.load(f)
        return data

    except TypeError as e:
        print(f"File Not Found {e}")
        raise
    except FileNotFoundError as e:
        print(f"File Not Found {e}")
        raise
    except Exception as e:
        print(e)
        raise



def print_json(data):
    for line in data:
        print(line["question"])
        print(line["answer"] + "\n")
        


def test():
    finetune("test","db_query")

if __name__ == "__main__":
    test()