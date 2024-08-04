from pyrogram import Client, filters, idle
from pyrogram.types import Message
import requests
import os

ADMIN_USER_ID = 1331278972

bot = Client(
    "Yordamchi [info]",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    in_memory=True,
)


@bot.on_message(filters.incoming & filters.private & filters.command("logs"))
async def logs(_, message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        return
    requests.get("https://yordamchi.greensmoke-1e04616b.westeurope.azurecontainerapps.io/logs")
    await bot.send_document(ADMIN_USER_ID, "yordamchi-service.log")


@bot.on_message(filters.incoming & filters.private & filters.command("snapshot"))
async def screenshot(_, message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        return
    await bot.send_photo(ADMIN_USER_ID, "screenshot.png")
    await bot.send_document(ADMIN_USER_ID, "page_source.html")


if __name__ == "__main__":
    bot.start()
    bot.send_message(ADMIN_USER_ID, "@yordamchi_info_bot restarted")
    idle()
