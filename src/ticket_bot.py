import support
from json_tools import load_json

import discord
from discord.ext import commands
from discord import app_commands

import os
import sys
from dotenv import load_dotenv

class TicketBot(commands.Bot):
    def __init__(self,json_path: str):
        self.Token = self._get_token()
        intents = discord.Intents.default()
        
        

        json_data = load_json(json_path)
        self.model_name = json_data["model"]
        self.ticket_channel = json_data["ticket_channel"]
        self.log_channel = json_data["log_channel"]
        self.prefix = json_data["prefix"]
        self.ticket_message_id = json_data["ticket_message"]
        self.ticket_message_content = json_data["ticket_message_content"]
        self.ticket_message_header = json_data["ticket_message_header"]
        
        super().__init__(command_prefix=self.prefix, intents=intents)
        

        #self.support_bot = self.create_support_bot(self.model_name)


    def _get_token(self):
        load_dotenv()
        return os.getenv("TOKEN")
    


    def create_support_bot(self,model_name = "meta-llama/Llama-3.2-1B-Instruct"):
        return support.Support(llm_model=model_name)
    

    def run_bot(self):
        try:     
            self.run(self.Token)
        except Exception as e:
            raise

    
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        synced = await self.tree.sync()
        print(f"🔁 Synced {len(synced)} command(s).")



    











def test():
    json_path = "..//inputs.json"
    bot = TicketBot(json_path)
    bot.run_bot()



if __name__ == "__main__":
    test()