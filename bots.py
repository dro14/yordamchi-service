from search import make_url, google_search, clean_data
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import os

yordamchi = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"]
)

google = Client(
    "Google",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    parse_mode=ParseMode.DISABLED,
)


@google.on_message(filters.private & filters.command("start"))
def start(_, message):
    message.reply_text("Hello! I'm a bot that can search on Google. Send me a keyword to search.")


@google.on_message(filters.private & filters.text)
def search(_, message):
    url = make_url("en", message.text)
    elements = google_search(url)
    results = clean_data(elements, with_links=True)
    message.reply_text(
        "\n\n".join(results)[:4096],
        disable_web_page_preview=True,
    )


yordamchi.start()
google.start()
