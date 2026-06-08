import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

class Bot(commands.Bot):
    async def on_reaction_added(self, reaction, user):
        if user.bot: return
        m = reaction.message
        self.channels_info[m.channel.id] = m.channel
        
    async def on_message(self, message):
        print(f"DEBUG: Message received from {message.author}: '{message.content}'")
        if message.author == self.user:
            return
        
        is_dm = message.guild is None
        is_mentioned = self.user.mentioned_in(message)
        print(is_dm)

        if is_dm or is_mentioned:
            self.last_message = message
            images = []
            if message.attachments:
                for i in message.attachments:
                    if i.content_type and i.content_type.startswith("image"):
                        images.append(i)

            self.channels_info[message.channel.id] = message.channel
            
        await self.process_commands(message)

    async def send_message(self, send_to_channel, message): await self.channels_info[send_to_channel].send(message)
    async def add_reaction(self, reaction): await self.last_message.add_reaction(reaction)
