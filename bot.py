from pyrogram import Client, filters, idle
from pyrogram.types import Message
import requests
import os

ADMIN_USER_ID = 1331278972

bot = Client(
    "Yordamchi [info]",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["INFO_BOT_TOKEN"],
    in_memory=True,
)


async def send_log_file():
    await bot.send_document(ADMIN_USER_ID, "yordamchi-service.log")


@bot.on_message(filters.incoming & filters.private & filters.command("logs"))
async def logs(_, message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        return
    requests.get("https://yordamchi.icysky-10e92f2c.westeurope.azurecontainerapps.io/logs")
    await send_log_file()


if __name__ == "__main__":
    bot.start()
    bot.send_message(ADMIN_USER_ID, "@yordamchi_info_bot restarted")
    idle()
