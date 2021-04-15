import time

from telethon import TelegramClient, events
from telethon.errors.common import MultiError
from config import *
from asyncio import run
from bot.mods.sql import DB

database = DB()
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
on_wait_users = {}
pm_start = """
Hello {}!, I'm {}
I'm a bot made by @cytolytic that scans groups and stores the users inside of them.
use /help for more info
"""

help_text = """
you can send me any user's id or username and I'll show you what groups he's in!
if I don't have that user, then you could scan some chats/channels to see if he's in some of them!
use /scan <(chat/channel)'s username or id> and I'll scan that chat/channel.
use /source to see how my owner made me.
use /support if you encounter any issues.
use /donate if you'd like to donate to my owner.
NOTE: this bot can be only used in pms for obvious reasons.
"""


def timer(func):
    async def wrapper(event, *args, **kwargs):
        if event.sender_id not in on_wait_users.keys():
            return await func(event, *args, **kwargs)
        user_time = on_wait_users[event.sender_id]
        if (user_time - time.time()) < 30*60:
            return await event.reply(f"sorry but you can't use this bot for another {int((30 * 60 - int(time.time() - user_time)) / 60)} minute(s)")
    return wrapper


@client.on(events.NewMessage(incoming=True, pattern=r"^\/start$"))
async def start(event):
    await event.reply(pm_start.format(event.sender.first_name, "@GroupScannerRobot"))


@client.on(events.NewMessage(incoming=True, pattern=r"^\/help"))
async def help(event):
    if not event.is_private:
        return await event.reply("contact me in pm.")
    await event.reply(help_text)


@client.on(events.NewMessage(incoming=True, pattern=r"^\/source$"))
async def source(event):
    await event.reply("https://github.com/cytoo/TgGroupScanner")


@client.on(events.NewMessage(incoming=True, pattern=r"^\/support"))
async def source(event):
    await event.reply(f"@{(await client.get_entity(SUPPORT_GROUP)).username}")


@client.on(events.NewMessage(incoming=True, pattern=r"^\/donate"))
async def source(event):
    await event.reply(f"you can donate to my owner [here](https://paypal.me/cytolytic)", link_preview=False)


@client.on(events.NewMessage(incoming=True))
async def query_user(event):
    if not event.is_private:
        return
    if not event.text or event.text.startswith("/"):
        return
    try:
        data = await client.get_entity(event.text)
    except ValueError:
        return await event.reply(f"cannot find entity with the value of {event.text}")
    res = await database.get_user(data.id)
    if not res:
        return await event.reply(
            f"the user {data.first_name} doesn't seem to exist in my db.\n it seems like I haven't "
            f"scanned a chat that he's in.\nyou can scan chats using /scan")
    return_text = f"User has been found!\n\n"
    return_text += f"username: {data.username if data.username else 'null'}\n" \
                   f"first name: {data.first_name}\n" \
                   f"last name: {data.last_name if data.last_name else 'null'}\n" \
                   f"id: {data.id}\n\n" \
                   f"total groups/channels found: {len(res)}\n\n"
    for _, _, chat in res:
        chat_data = await client.get_entity(int(chat))
        return_text += f"~ {chat_data.title} | {'@' + chat_data.username if chat_data.username else 'no username'}\n"
    return_text += "\ndata by @GroupScannerRobot\n"
    return_text += f"join @{(await client.get_entity(SUPPORT_GROUP)).username}"
    await event.reply(return_text)


@client.on(events.NewMessage(incoming=True, pattern=r"^\/scan (.*)"))
@timer
async def scan(event):
    if not event.is_private:
        return
    look_for = event.pattern_match.group(1)
    if not len(look_for) > 4:
        return await event.reply("that chat doesn't seem to exist! send me a chat's username or id.")
    try:
        look_for = int(look_for)
    except ValueError:
        pass
    try:
        data = client.iter_participants(look_for, aggressive=True)
    except ValueError:
        return await event.reply("the chat you sent doesn't seem to exist.")
    chat = await client.get_entity(look_for)
    on_wait_users.update({event.sender_id: time.time()})
    try:
        async for user in data:
            await database.insert_user(
                user.id,
                user.username if user.username else "null",
                chat.id
            )
    except MultiError:
        await event.reply("sorry, but I can't scan that chat/channel ;-;")
        return
    await event.reply(f"{chat.id} has been scanned.")