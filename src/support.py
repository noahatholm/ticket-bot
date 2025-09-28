from finetuning.lm import Model
from finetuning.lora import fetch_prompt
from rag.rag_class import Rag



#This class combines rag and the lm into one class

class Support:
    def __init__(self,*, 
                 image_folder = "..//rag//images",
                 corpus_folder = "..//corpus//", 
                 embedding_model = "all-MiniLM-L6-v2",
                 llm_model = "meta-llama/Llama-3.2-1B-Instruct",
                 path_to_adaptors = "..//models/",
                 path_to_finetune = "..//finetuning/",
                 path_to_prompts = "..//prompts/",

                 ):
        self.llmModel = Model(model_name=llm_model,
                              path_to_adaptors=path_to_adaptors,
                              path_to_finetune=path_to_finetune,
                              path_to_prompts=path_to_prompts)
        self.rag = Rag(image_folder,corpus_folder,model_name=embedding_model)

        #Store path attributes
        self.path_to_adaptors = path_to_adaptors
        self.path_to_prompts = path_to_prompts
        self.path_to_finetune = path_to_finetune

    def set_adaptor(self,name):
        try:
            self.llmModel.set_adaptor(name)
        except:
            raise

    def user_query_to_rag_query(self,query):
        tokens = 30
        self.llmModel.set_adaptor("db_query")
        prompt = fetch_prompt("db_query",path_to_folder=self.path_to_prompts)
        prompt = prompt.format(query)
        

        #Query Model
        response = self.llmModel.query(prompt,tokens=tokens)
        return self.llmModel.extract_answer(response)

    def query_llm_for_support(self,conversation,*,rag_data = ""):
        prompt = self.add_system_prompt(conversation,rag_data)
        response = self.llmModel.query_chat_prompt(prompt,tokens=300)
        return response


        #Adds a system prompt as well as some rag information
    def add_system_prompt(self,conversation,rag_information):
        system_prompt = fetch_prompt("support",self.path_to_prompts)
        user_prompt = fetch_prompt("user_prompt",self.path_to_prompts)
        userQuery = self.conversation_to_text(conversation)

        user_prompt = user_prompt.format(rag_information["text"],userQuery)
        formatted_prompt = [{"role":"system","content":system_prompt}]
        formatted_prompt.append({"role":"user","content":user_prompt})
        return formatted_prompt



    #Takes a conversation (without system prompt) in openais system, user template format and returns next message and images
    def provide_support(self,conversation): 
        text_conversation = self.conversation_to_text(conversation) 
        rag_query = self.user_query_to_rag_query(text_conversation)
        #print(rag_query)
        rag_data = self.rag.query(rag_query)
        response = self.query_llm_for_support(conversation,rag_data=rag_data)
        return response


    def conversation_to_text(self,conversation):
        text = ""
        for message in conversation:
            text += f"{message["role"]}: {message["content"]}\n"
        return text





def test():
    ticket_support = Support()
    conversation = [
        {"role": "user",
         "content": "Help my router isn't working its showing a flashing red light?"}
    ]
    print(ticket_support.provide_support(conversation))


if __name__ == "__main__":
    test()

    
