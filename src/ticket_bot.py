import support
from json_tools import load_json, save_button,load_button
from ticket_tools import create_ticket

import discord
from discord.ext import commands
from discord import app_commands


import os
import sys
from dotenv import load_dotenv
import asyncio

class Ticket_Button(discord.ui.View):
    def __init__(self,label,support_Bot,*,category=None,support_role=None):
        super().__init__(timeout=None)  # timeout=None keeps the button active forever
        self.label = label
        self.support_Bot = support_Bot
        self.category = category
        self.support_role = support_role

        button = discord.ui.Button(
            label=self.label,
            style=discord.ButtonStyle.primary,
            custom_id="ticket_button"
        )
        button.callback = self.create_ticket
        self.add_item(button)


    async def create_ticket(self,interaction:discord.Interaction):
        await create_ticket(interaction,self.support_Bot,category=self.category,support_role = self.support_role)  # link to callback
        






class TicketBot(commands.Bot):
    def __init__(self,json_path: str):
        self.Token = self._get_token()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        

        json_data = load_json(json_path)
        self.model_name = json_data["model"]
        self.log_channel = json_data["log_channel"]
        self.prefix = json_data["prefix"]
        self.ticket_category = json_data["ticket_category"]
        self.support_role = json_data["support_role"]

        
        super().__init__(command_prefix=self.prefix, intents=intents)
        
        #Load Button Data
        self.path_to_button = "..//button.json"
        button_data = load_button(self.path_to_button)
            
        self.ticket_channel_id = button_data["channel_id"]
        self.ticket_message_id = button_data["message_id"]
        self.ticket_message_content = button_data["message_content"]
        self.ticket_message_header = button_data["message_header"]
        self.ticket_message_button = button_data["message_button"]        

        
        self.support_bot = self.create_support_bot(self.model_name)


    def _get_token(self):
        load_dotenv()
        return os.getenv("TOKEN")
    


    def create_support_bot(self,model_name = "meta-llama/Llama-3.2-1B-Instruct"):
        return support.Support(llm_model=model_name)
    
    def build_button_data(self):
        return {
            "channel_id": self.ticket_channel_id,
            "message_id": self.ticket_message_id,
            "message_header": self.ticket_message_header,
            "message_content": self.ticket_message_content,
            "message_button": self.ticket_message_button
        }

    
    async def setup_hook(self):
        @self.tree.command(name="setup", description="Sends an Embed to a channel to create tickets")
        async def setup(interaction: discord.Interaction):
            embed = discord.Embed(
                title=interaction.client.ticket_message_header,
                description=interaction.client.ticket_message_content,
                color=discord.Color.blurple()
            )
            view = Ticket_Button(
                interaction.client.ticket_message_button, 
                interaction.client.support_bot,
                category=interaction.client.ticket_category
            )
            await interaction.response.send_message(embed=embed, view=view)

        @self.tree.command(name="close", description="Closes a Ticket")
        async def close(interaction: discord.Interaction):
            if not interaction.channel.name.startswith("ticket"):
                await interaction.response.send_message("This channel isn't a ticket")
                return
            
            await interaction.response.send_message("Successfully Closed Ticket closing ticket in 3 seconds")
            await asyncio.sleep(3)
            await interaction.channel.delete()
            return


        self.add_view(Ticket_Button(self.ticket_message_button, self.support_bot, category=self.ticket_category,support_role=self.support_role))
        
        # Save button data to disk
        save_button(self.path_to_button, self.build_button_data())

        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    def run_bot(self):
        try:
            self.run(self.Token)
        except Exception as e:
            raise



    











def test():
    json_path = "..//inputs.json"
    bot = TicketBot(json_path)
    bot.run_bot()



if __name__ == "__main__":
    test()