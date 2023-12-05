from search import make_url, google_search, clean_data
from contextlib import asynccontextmanager
from vectordb import client, retriever
from fastapi import FastAPI, Request
from loaders import load_document
import pyrogram
import uvicorn
import os

uuids = {}
file_names = {}


def clear(user_id):
    try:
        uuids[user_id]
    except KeyError:
        pass
    else:
        for uuid in uuids[user_id]:
            client.data_object.delete(uuid, class_name="LangChain")
        uuids.pop(user_id)


bot = pyrogram.Client(
    "my_account",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)


@asynccontextmanager
async def lifespan(_):
    await bot.start()
    yield
    await bot.stop()


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
    await bot.download_media(file_id, file_name)

    try:
        docs = load_document(file_name, user_id)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    else:
        clear(user_id)
        uuids[user_id] = retriever.add_documents(docs)
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
        url = make_url(lang, query)
        elements = google_search(url)
        results = clean_data(elements, with_links=False)
        return {"results": "\n\n".join(results)}
    else:
        docs = retriever.get_relevant_documents(
            query,
            where_filter={
                "path": ["user_id"],
                "operator": "Equal",
                "valueNumber": user_id,
            },
        )
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
        return {"file_name": "Google"}
    else:
        return {"file_name": file_name}


@app.post("/delete")
async def delete(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    clear(user_id)
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", log_level="warning")
