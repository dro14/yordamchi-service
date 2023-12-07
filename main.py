from search import make_url, google_search, clean_data
from contextlib import asynccontextmanager
from vectordb import client, retriever
from fastapi import FastAPI, Request
from loaders import load_document
from pyrogram import Client
import subprocess
import uvicorn
import time
import os

uuids = {}
file_names = {}


async def clear(user_id):
    try:
        uuids[user_id]
    except KeyError:
        pass
    else:
        for uuid in uuids[user_id]:
            client.data_object.delete(uuid, class_name="LangChain")
        uuids.pop(user_id)
        file_names.pop(user_id)


yordamchi = Client(
    "Yordamchi",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["MAIN_BOT_TOKEN"]
)


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
    data = await request.json()
    file_id = data["file_id"]
    file_name = data["file_name"]
    user_id = data["user_id"]
    await yordamchi.download_media(file_id, file_name)

    try:
        docs = await load_document(file_name, user_id)
    except Exception as e:
        return {"success": False, "error": str(e)}
    else:
        await clear(user_id)
        doc_ids = []
        for i, doc in enumerate(docs):
            doc_ids.extend(retriever.add_documents([doc]))
            if i % 10 == 0:
                time.sleep(0.1)
        uuids[user_id] = doc_ids
        file_names[user_id] = file_name
        return {"success": True}


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data["query"]
    lang = data["lang"]
    user_id = data["user_id"]

    try:
        uuids[user_id]
    except KeyError:
        url = await make_url(lang, query)
        elements = await google_search(url)
        results = await clean_data(elements, with_links=False)
        return {"results": "\n\n".join(results)}
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
        return {"results": "\n\n".join(results)}


@app.post("/memory")
async def memory(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    try:
        file_name = file_names[user_id]
    except KeyError:
        return {"source": "Google"}
    else:
        return {"source": file_name}


@app.post("/delete")
async def delete(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    await clear(user_id)
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
