from functions import google_search, clean_data
from fastapi import FastAPI, Request


app = FastAPI()


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data["query"]
    if query:
        elements = google_search(query)
        results = clean_data(elements)
        return {"results": results}
    else:
        return {"error": "No query provided"}
