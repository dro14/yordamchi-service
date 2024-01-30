from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from urllib.parse import quote
import os

options = FirefoxOptions()
options.add_argument("--headless")
driver = Firefox(options=options)
driver.implicitly_wait(0.5)


def google_search(query: str) -> set[str]:
    url = f"https://www.google.com/search?hl=en&gl=uz&num=5&q={quote(query)}"
    driver.get(url)

    try:
        driver.find_element(By.ID, "L2AGLb").click()
    except NoSuchElementException:
        pass

    elements = []
    try:
        elements.extend(driver.find_elements(By.CLASS_NAME, "Kot7x"))
    except NoSuchElementException:
        pass
    try:
        elements.extend(driver.find_elements(By.CLASS_NAME, "MjjYud"))
    except NoSuchElementException:
        pass

    results = set()
    for element in elements:
        if not element.text.strip():
            continue

        lines = element.text.splitlines()
        i = 0
        while i < len(lines):
            lines[i] = lines[i].strip()
            if lines[i].startswith(("http", "·", "•")):
                lines.pop(i)
            else:
                i += 1

        try:
            link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        except NoSuchElementException:
            pass
        else:
            lines.append(link)

        results.add("\n".join(lines))

    return results


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
    results = google_search(message.text)
    await message.reply_text("\n\n".join(results)[:4096], disable_web_page_preview=True)


if __name__ == "__main__":
    google.start()
    google.send_message(1331278972, "@web_searching_bot restarted")
    idle()
