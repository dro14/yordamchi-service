from vectordb import retriever, users, clear
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from threading import Thread, Event
from loaders import load_document
from bot import ADMIN_USER_ID
from pyrogram import Client
from typing import Callable
from search import search
import tracemalloc
import subprocess
import uvicorn
import asyncio
import sys
import os

tracemalloc.start()
log_file = open("yordamchi-service.log", "w")
sys.stdout = log_file
sys.stderr = log_file

bot = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"],
    in_memory=True,
)


@asynccontextmanager
async def lifespan(_):
    await bot.start()
    google = subprocess.Popen(["python", "bot.py"], stdout=log_file, stderr=log_file)
    yield
    await bot.stop()
    google.terminate()


app = FastAPI(lifespan=lifespan)


def load_thread(data: dict, response: dict, done: Event) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    file_id = data["file_id"]
    file_name = data["file_name"].replace(" ", "_")
    user_id = data["user_id"]
    bot.download_media(file_id, file_name)

    try:
        docs = load_document(file_name, user_id)
    except Exception as e:
        response["success"] = False
        response["error"] = str(e)
        if not response["error"].startswith("unsupported file format"):
            print(f"error while loading a file: {response['error']}")
    else:
        clear(user_id)
        uuids = retriever.add_documents(docs)
        users[user_id] = {"uuids": uuids, "file_name": file_name}
        response["success"] = True

    done.set()
    loop.close()


async def respond(request: Request, target: Callable[[dict, dict, Event], None]) -> dict:
    data = await request.json()
    response = {}
    done = Event()
    engine = Thread(target=target, args=(data, response, done))
    engine.start()
    while not done.wait(0.005):
        await asyncio.sleep(0.095)
    engine.join()
    return response


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/load")
async def load(request: Request):
    return await respond(request, load_thread)


@app.post("/file_search")
async def file_search(request: Request):
    data = await request.json()
    query = data["query"]
    user_id = data["user_id"]

    if user_id not in users:
        return {"success": False, "error": "no documents loaded"}

    where_filter = {
        "path": ["user_id"],
        "operator": "Equal",
        "valueNumber": user_id,
    }
    docs = retriever.get_relevant_documents(query, where_filter=where_filter)
    results = set()
    for doc in docs:
        results.add(doc.page_content)
    return {"success": True, "results": "\n\n".join(results)}


@app.post("/google_search")
async def google_search(request: Request):
    data = await request.json()
    query = data["query"]
    lang = data["lang"]

    try:
        results = search(query, lang)
    except Exception as e:
        return {"success": False, "error": str(e)}
    else:
        return {"success": True, "results": "\n\n".join(results)}


@app.post("/memory")
async def memory(request: Request):
    data = await request.json()
    user_id = data["user_id"]

    try:
        user = users[user_id]
    except KeyError:
        source = "GOOGLE"
    else:
        source = user["file_name"]

    return {"source": source}


@app.post("/delete")
async def delete(request: Request):
    data = await request.json()
    user_id = data["user_id"]

    try:
        clear(user_id)
    except Exception as e:
        return {"success": False, "error": str(e)}
    else:
        return {"success": True}


@app.post("/files")
async def files(request: Request):
    data = await request.json()
    user_id = data["user_id"]

    if user_id != ADMIN_USER_ID:
        return {"success": False, "error": "forbidden"}

    sources = ""
    for user_id, user in users.items():
        sources += f"{user_id}:\t{user['file_name']}\n"
    return {"success": True, "files": sources}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
