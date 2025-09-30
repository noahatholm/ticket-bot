#This document provides a wrapper class that will finetune and query the language model
from .lora import finetune,fetch_prompt

from dotenv import load_dotenv
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel,get_peft_model
import re


class Model():
    def __init__(self, *,
        model_name = "meta-llama/Llama-3.2-1B-Instruct",  
        device = "cuda",
        dtype = torch.float16,#Using float16 because uni gpu isn't designed for bfloats
        path_to_adaptors = "..//..//models/",
        path_to_finetune = "..//..//finetuning/",
        path_to_prompts = "..//..//prompts/"
    ):  
        self.model_name = model_name
        self.device = device
        self.dtype = dtype

        #Paths
        self.path_to_adaptors = path_to_adaptors
        self.path_to_prompts = path_to_prompts
        self.path_to_finetune = path_to_finetune



        #Define our llm
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name,
                                                          device_map=self.device,
                                                          dtype=self.dtype)
        
        #Define our tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name,
                                                       token = self._get_Hugging_Face_API(),
                                                       padding_side = "left")
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def get_model(self):
        return self.model

    def get_tokenizer(self):
        return self.tokenizer

    def get_LoRA_models(self):
        return self.LoRA_models
    
    def _get_Hugging_Face_API(self):
        load_dotenv("..")
        os.getenv("HUGGINGAPI")



    def set_adaptor(self,name):
        try:
            if not os.path.exists(self.path_to_adaptors + name + "//adapter_config.json"): #Check if lora already exists
                if not finetune(self.model,self.tokenizer,"db_query","db_query",epochs = 10, device="cuda",path_to_prompt=self.path_to_prompts, path_to_finetune=self.path_to_finetune, path_to_adaptors = self.path_to_adaptors): #If not create one
                    print("Finetune Returned False")

            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, #Load adaptor
                device_map=self.device,
                dtype=self.dtype)
            self.model = PeftModel.from_pretrained(self.model, self.path_to_adaptors + name)
            print("Adaptor Set to " + name)
        except Exception as e:
            print(e)
            raise

    def reset_adaptor(self):
        try:
            self.model = self.model.get_base_model()
            print("Model Reset to Base")
        except Exception as e:
            print(e)
            raise

    #Pads and tokenizes a text prompt
    def tokenize_prompt(self,prompt):
        return self.tokenizer(prompt,padding=True,return_tensors = "pt").to(self.device)
        

    #Pads and tokenizes a prompt using openais system, user template
    def tokenize_chat_prompt(self,prompt):
        return self.tokenizer.apply_chat_template(prompt,padding=True,return_tensors="pt",add_generation_prompt=True).to(self.device)

    #Generate wrapper with my preset values that i found work better
    def generate(self,tokenized_prompt,*, newTokens = 200, temperature = 0.15, top_p = 0.9, top_k = 40, repetition_penalty=1.1,do_sample=True):
        pad_token_id = self.tokenizer.eos_token_id
        return self.model.generate(
            input_ids=tokenized_prompt["input_ids"], 
            attention_mask=tokenized_prompt['attention_mask'],
            max_new_tokens=newTokens,
            temperature=temperature, 
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample, 
            pad_token_id=pad_token_id,
            eos_token_id=pad_token_id)

    def generate_conversation(self,tokenized_prompt,*, newTokens = 200, temperature = 0.15, top_p = 0.9, top_k = 40, repetition_penalty=1.1,do_sample=True):
        pad_token_id = self.tokenizer.eos_token_id
        return self.model.generate(tokenized_prompt,
                                    max_new_tokens = newTokens,
                                    do_sample = do_sample,
                                    top_p=top_p,
                                    top_k=top_k,
                                    repetition_penalty=repetition_penalty, 
                                    pad_token_id=pad_token_id,
                                    eos_token_id=pad_token_id)

    def decode(self,tokens,length):
        return self.tokenizer.decode(tokens[0,length:])
    
    def batch_decode(self,tokens,length):
        return self.tokenizer.batch_decode(tokens)[0]

    #Basic lm text generation
    def query(self,prompt,*,tokens = 200, finetuned = None):
        tokenized_prompt = self.tokenize_prompt(prompt)
        generated_tokens = self.generate(tokenized_prompt,newTokens = tokens)
        decoded_tokens = self.decode(generated_tokens,len(tokenized_prompt))
        #print(decoded_tokens)
        return decoded_tokens
    

        #Conversation lm text generation
    def query_chat_prompt(self,prompt,*,tokens = 300, finetuned = None):
        tokenized_prompt = self.tokenize_chat_prompt(prompt)
        generated_tokens = self.generate_conversation(tokenized_prompt,newTokens = tokens)
        decoded_tokens = self.batch_decode(generated_tokens,len(tokenized_prompt))
        #print(decoded_tokens)
        return decoded_tokens


    def extract_answer(self,text):
        matches = re.findall(r'<Answer>(.*?)</Answer>', text, flags=re.DOTALL)
        return[matches[1]]

def test():
    myModel = Model()

    prompt = fetch_prompt("db_query","..//..//prompts/")
    query = "Help my router isn't working its showing a flashing red light?"
    prompt = prompt.format(query)
    print(prompt)


    print(myModel.query(prompt, tokens = 100))

    #finetune(myModel.get_model(),myModel.get_tokenizer(),"db_query","db_query",epochs = 5, device="cuda")



    myModel.set_adaptor("db_query")
    print("####################")


    print(response := myModel.query(prompt, tokens = 30))

    print("#####################")

    print(myModel.extract_answer(response))

    #print(myModel.query("what is the capital of england?", tokens = 20))


if __name__ == "__main__":
    test()