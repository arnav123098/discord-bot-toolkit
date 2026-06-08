import discord

class Event:
    def __init__(self, event_type: str, raw):
        self.type = event_type
        self.id = getattr(raw, 'id', None)

        if hasattr(raw, 'author'):
            self.user = raw.author
        else:
            self.user = getattr(raw, 'user', None)
        self.channel = getattr(raw, 'channel', None)

        self.timestamp = (getattr(raw, 'timestamp', None) or getattr(raw, 'created_at', None))

        self.guild = getattr(raw, 'guild', None)
        self.raw = raw

    @property
    def is_dm(self) -> bool: return self.guild is None

    @property
    def is_guild(self) -> bool: return self.guild is not None

class Message(Event):
    def __init__(self, raw: discord.Message):
        super().__init__("message", raw)

        self.is_reply = raw.reference is not None
        self.reference_id = raw.reference.message_id if self.is_reply else None

        self.mentions = [user.id for user in raw.mentions]

        self.text = raw.content
        self.images = []
        self.videos = []
        self.audio = []
        self.files = []

        self._extract_attachments()

    def _extract_attachments(self) -> None:
        for a in self.raw.attachments:
            content_type = a.content_type or ""

            if content_type.startswith('image/'):
                self.images.append(Image(a))
            elif content_type.startswith('video/'):
                self.videos.append(Video(a))
            elif content_type.startswith('audio/'):
                self.audio.append(Audio(a))
            else:
                self.files.append(File(a))

    @property
    def has_attachments(self):
        return bool(self.attachments)

    @property
    def attachments(self) -> list:
        return [
            *self.images,
            *self.videos,
            *self.audio,
            *self.files,
        ]
    
    def set_is_me(self, bot_user) -> None:
        self.is_me = bot_user == self.user
    
    async def reply(self, content) -> discord.Message:
        return await self.channel.send(
            content,
            reference=self.raw
        )

class Attachment:
    def __init__(self, raw: discord.Attachment):
        self.raw = raw

        self.content_type = raw.content_type
        self.proxy_url = raw.proxy_url

        self.filename = raw.filename
        self.url = raw.url
        self.size = raw.size

        self.is_spoiler = raw.is_spoiler()
        self.is_ephemeral = raw.ephemeral

    async def read(self):
        return await self.raw.read()

    async def save(self, path):
        await self.raw.save(path)

class Image(Attachment):
    type = "image"
    def __init__(self, raw: discord.Attachment):
        super().__init__(raw)

        self.description = raw.description
        self.height = raw.height
        self.width = raw.width

class Video(Attachment):
    type = "video"
    def __init__(self, raw: discord.Attachment):
        super().__init__(raw)

        self.height = raw.height
        self.width = raw.width

        self.duration = getattr(raw, "duration", None)
        
class Audio(Attachment):
    type = "audio"
    def __init__(self, raw: discord.Attachment):
        super().__init__(raw)

        self.duration = getattr(raw, "duration", None)
        self.waveform = getattr(raw, "waveform", None)

class File(Attachment):
    type = "file"
    def __init__(self, raw: discord.Attachment):
        super().__init__(raw)

class Reaction(Event):
    def __init__(self, raw: discord.Reaction):
        super().__init__("reaction", raw)

        self.emoji = raw.emoji
        self.count = raw.count
        self.reference = Message(raw.message)

        self.is_me = raw.me

    @property
    def users(self): return self.raw.users()

    async def add(self, emoji) -> None:
        if self.is_me: return
        await self.reference.raw.add_reaction(emoji)

    async def remove(self, user) -> None: await self.raw.remove(user)

class Typing(Event): # unsure about this (will find out after testing)
    def __init__(self, raw: discord.RawTypingEvent):
        super().__init__("typing", raw)
