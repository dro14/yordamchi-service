from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from search import google_search
import os

google = Client(
    "Google",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    in_memory=True,
    parse_mode=ParseMode.DISABLED,
)


@google.on_message(filters.incoming & filters.private & filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("Hello!\nI'm a bot that can search on Google.\nSend me a query to search.")


@google.on_message(filters.incoming & filters.private & filters.command("logs"))
async def logs(_, message: Message):
    await google.send_document(message.from_user.id, "yordamchi-service.log")


@google.on_message(filters.incoming & filters.private & filters.text)
async def search(_, message: Message):
    results = google_search(message.text, "en", True)
    await message.reply_text("\n\n".join(results)[:4096], disable_web_page_preview=True)


if __name__ == "__main__":
    google.start()
    google.send_message(1331278972, "@web_searching_bot restarted")
    idle()
