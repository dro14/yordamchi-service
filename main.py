from vectordb import retriever, users, clear
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from threading import Thread, Event
from loaders import load_document
from search import google_search
from pyrogram import Client
from typing import Callable
import tracemalloc
import subprocess
import uvicorn
import asyncio
import sys
import os

tracemalloc.start()
sys.stdout = open("yordamchi-service.log", "w")
sys.stderr = sys.stdout

yordamchi = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"],
    in_memory=True,
)


def load_thread(data: dict, response: dict, done: Event) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    file_id = data["file_id"]
    file_name = data["file_name"]
    user_id = data["user_id"]
    yordamchi.download_media(file_id, file_name)

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


def search_thread(data: dict, response: dict, done: Event) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    query = data["query"]
    lang = data["lang"]
    user_id = data["user_id"]

    try:
        users[user_id]
    except KeyError:
        results = google_search(query, lang, False)
    else:
        where_filter = {
            "path": ["user_id"],
            "operator": "Equal",
            "valueNumber": user_id,
        }
        docs = retriever.get_relevant_documents(query, where_filter=where_filter)
        results = set()
        for doc in docs:
            results.add(doc.page_content)

    response["results"] = "\n\n".join(results)
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


@asynccontextmanager
async def lifespan(_):
    Thread(target=subprocess.run, args=(["python", "google.py"],)).start()
    await yordamchi.start()
    yield
    await yordamchi.stop()


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
        source = "Google"
    else:
        source = user["file_name"]

    if user_id == 1331278972:
        for user_id, user in users.items():
            source += f"\n{user_id}: {user['file_name']}"

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


@app.post("/logs")
async def logs(request: Request):
    data = await request.json()
    user_id = data["user_id"]

    if user_id != 1331278972:
        return {"success": False, "error": "forbidden"}

    completed_process = subprocess.run(["python", "yordamchi.py"])
    if completed_process.stderr:
        return {"success": False, "error": completed_process.stderr.decode()}
    elif completed_process.stdout:
        return {"success": False, "error": completed_process.stdout.decode()}
    elif completed_process.returncode:
        return {"success": False, "error": f"unknown error: return code {completed_process.returncode}"}
    else:
        return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
