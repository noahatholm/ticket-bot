#This document provides a wrapper class that will finetune and query the language model
from lora import finetune,fetch_prompt

from dotenv import load_dotenv
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel,get_peft_model


class Model():
    def __init__(self,*,model_name = "meta-llama/Llama-3.2-1B-Instruct", #A larger model is optimal however im developing on an old gpu
                  device = "cuda",
                    dtype = torch.float16): #Using float16 because uni gpu isn't designed for bfloats
        self.model_name = model_name
        self.device = device
        self.dtype = dtype




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
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name,
                device_map=self.device,
                dtype=self.dtype)
            self.model = PeftModel.from_pretrained(self.model, "../models/" + name)
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
            do_sample=True, 
            pad_token_id=pad_token_id,
            eos_token_id=pad_token_id)

    def decode(self,tokens):
        return self.tokenizer.batch_decode(tokens)

    #Basic lm text generation
    def query(self,prompt,*,tokens = 200, finetuned = None):
        tokenized_prompt = self.tokenize_prompt(prompt)
        generated_tokens = self.generate(tokenized_prompt,newTokens = tokens)
        decoded_tokens = self.decode(generated_tokens)
        return decoded_tokens[-len(prompt):]



def test():
    myModel = Model()

    prompt = fetch_prompt("db_query")
    query = "Help my router isn't working its showing a flashing red light?"
    prompt = prompt.format(query)
    print(prompt)


    print(myModel.query(prompt, tokens = 100))

    finetune(myModel.get_model(),myModel.get_tokenizer(),"db_query","db_query",epochs = 5, device="cuda")



    myModel.set_adaptor("db_query")

    print(myModel.query(prompt, tokens = 100))

    #print(myModel.query("what is the capital of england?", tokens = 20))


if __name__ == "__main__":
    test()