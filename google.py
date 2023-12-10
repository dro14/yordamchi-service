from search import make_url, google_search, clean_data
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
import os

google = Client(
    "Google",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    parse_mode=ParseMode.DISABLED,
)


@google.on_message(filters.incoming & filters.private & filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("Hello!\nI'm a bot that can search on Google.\nSend me a query to search.")


@google.on_message(filters.incoming & filters.private & filters.text)
async def search(_, message: Message):
    url = make_url("en", message.text)
    elements = google_search(url)
    results = clean_data(elements, True)
    await message.reply_text("\n\n".join(results)[:4096], disable_web_page_preview=True)


if __name__ == "__main__":
    google.run()
