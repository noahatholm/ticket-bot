import discord
from discord.utils import get
import asyncio
import support
from finetuning.lora import fetch_prompt

async def create_ticket(interaction: discord.Interaction, support_bot: support.Support,*,category = None,support_role = None):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("⚠️ This command can only be used in a server.", ephemeral=True)
            return

        if category:
            category = guild.get_channel(int(category))

        
        

        name = "Ticket-" + interaction.user.name

        permissions = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),  # hide from everyone
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

        if support_role:
            support_role = guild.get_role(int(support_role))
            permissions[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)


        # create the text channel
        if category:
            channel = await guild.create_text_channel(name,category=category,overwrites=permissions,reason=f"Support ticket for {interaction.user.name}")
        else:
             channel = await guild.create_text_channel(name,overwrites=permissions,reason=f"Support ticket for {interaction.user.name}")
        
        # respond to the user
        await interaction.response.send_message(f"✅ Text channel created: {channel.mention}")
        await ticket_support(interaction.client,channel,interaction.user.id,support_bot)
        return channel


async def ticket_support(client,ticket,user_id,support_bot: support.Support):
    def check(m: discord.Message):
        return (
            m.author.id == user_id 
            and m.channel == ticket 
            and m.content.strip() != ""
        )
    conversation = []
    await ticket.send(fetch_prompt("ticket_message","..//prompts//"))
    user_query = "halp"
    while user_query: #Ticket support loop, if no response for 5 min it times out
        user_query = await client.wait_for('message',check = check, timeout = 300) #5 min timeout
        await ticket.send("Thank you for contacting support. Please allow one moment")
        
        conversation.append({"role":"user","content":user_query.content})
        result = await asyncio.to_thread(support_bot.provide_support, conversation)
        conversation.append({"role":"system","content":result})
        print(result)

        await ticket.send(result[0])
        for file_name in result[1]: #Send relavent image
            await ticket.send(file = discord.File(file_name))
        

                      
    ##Wait for their response


