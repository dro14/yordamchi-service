from pyrogram import Client
import os

yordamchi = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"],
    in_memory=True,
)
yordamchi.start()
yordamchi.send_document(1331278972, "yordamchi-service.log")
yordamchi.stop()
