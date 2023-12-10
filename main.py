from search import make_url, google_search, clean_data
from vectordb import retriever, users, clear
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from threading import Thread, Event
from loaders import load_document
from pyrogram import Client
from typing import Callable
import subprocess
import uvicorn
import asyncio
import time
import os

UPLOAD_BATCH_SIZE = 10
UPLOAD_INTERVAL = 0.1

yordamchi = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"]
)


def load_thread(data: dict, response: dict, done: Event) -> None:
    file_id = data["file_id"]
    file_name = data["file_name"]
    user_id = data["user_id"]
    print(f"file_id: {file_id}", f"file_name: {file_name}", f"user_id: {user_id}", sep="\n")
    yordamchi.download_media(file_id, file_name)

    try:
        docs = load_document(file_name, user_id)
    except Exception as e:
        response["success"] = False
        response["error"] = str(e)
        print(f"error: {response['error']}")
    else:
        uuids = []
        left = 0
        right = UPLOAD_BATCH_SIZE
        while left < len(docs):
            uuids.extend(retriever.add_documents(docs[left:right]))
            left, right = right, right + UPLOAD_BATCH_SIZE
            time.sleep(UPLOAD_INTERVAL)
        clear(user_id)
        users[user_id] = {"uuids": uuids, "file_name": file_name}
        response["success"] = True

    print(f"success: {response['success']}")
    done.set()


def search_thread(data: dict, response: dict, done: Event) -> None:
    query = data["query"]
    lang = data["lang"]
    user_id = data["user_id"]
    print(f"query: {query}", f"lang: {lang}", f"user_id: {user_id}", sep="\n")

    try:
        users[user_id]
    except KeyError:
        url = make_url(lang, query)
        elements = google_search(url)
        results = clean_data(elements, False)
    else:
        where_filter = {
            "path": ["user_id"],
            "operator": "Equal",
            "valueNumber": user_id,
        }
        results = set()
        docs = retriever.get_relevant_documents(query, where_filter=where_filter)
        for doc in docs:
            results.add(doc.page_content)

    response["results"] = "\n\n".join(results)
    print(response["results"])
    done.set()


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


@asynccontextmanager
async def lifespan(_):
    await yordamchi.start()
    process = subprocess.Popen(["python", "google.py"])
    yield
    await yordamchi.stop()
    process.terminate()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/load")
async def load(request: Request):
    return await respond(request, load_thread)


@app.post("/search")
async def search(request: Request):
    return await respond(request, search_thread)


@app.post("/memory")
async def memory(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    try:
        user = users[user_id]
    except KeyError:
        return {"source": "Google"}
    else:
        return {"source": user["file_name"]}


@app.post("/delete")
async def delete(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    clear(user_id)
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
