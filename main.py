from functions import make_url, google_search, clean_data
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, Yordamchi!"}


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data["query"]
    lang = data["lang"]
    if query:
        url = make_url(lang, query)
        elements = google_search(url)
        results = clean_data(elements, with_links=False)
        return {"results": results}
    else:
        return {"error": "No query provided"}
