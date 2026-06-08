import discord
from discord.ext import commands
from discord_bot_toolkit.events import Message, Reaction, Typing
import asyncio

# TODO: test

# to start bot: self.run(token)
# to stop bot: self.close()

class Bot(commands.Bot):
    INTENTS = set(discord.Intents.VALID_FLAGS)

    def __init__(self, user_intents: list | None = None):
        user_intents = user_intents or []

        if 'all' in user_intents: 
            intents = discord.Intents.all()
        else:
            intents = discord.Intents.none()
            for intent in user_intents:
                if intent not in self.INTENTS:
                    raise ValueError(f"Invalid value for user_intents: {intent}")
                setattr(intents, intent, True)
        
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self._listeners = {
            "message": [],
            "message_edit": [],
            "reaction": [],
            "typing": []
        }

        self.message = self._register("message")
        self.message_edit = self._register("message_edit")
        self.reaction = self._register("reaction")
        self.typing = self._register("typing")

    async def to_listeners(self, listener_type: str, *events):
        results = await asyncio.gather(
            *(listener(*events) for listener in self._listeners[listener_type]),   
            return_exceptions=True
        )

        for res in results:
            if isinstance(res, Exception):
                print(res)

    def _register(self, event_name):
        def decorator(func):
            self._listeners[event_name].append(func)
            return func
        return decorator

    async def on_ready(self):
        print(f"Bot live as {self.user}") 

    async def on_message(self, msg):
        msg = Message(msg)
        msg.set_is_me(self.user)

        await self.to_listeners("message", msg)

    async def on_message_edit(self, before, after):
        before, after = Message(before), Message(after) 
        before.set_is_me(self.user)
        after.set_is_me(self.user)

        await self.to_listeners("message_edit", before, after)

    async def on_reaction_add(self, reaction, user):
        reaction = Reaction(reaction)
        reaction.user = user

        await self.to_listeners("reaction", reaction)

    async def on_raw_typing(self, event): # unsure about this for now
        event = Typing(event)
        
        await self.to_listeners("typing", event)

bot = Bot()

@bot.message
async def print_message(msg): print(msg)

# bot.start()
