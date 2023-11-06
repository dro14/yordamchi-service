from functions import make_url, google_search, clean_data
from fastapi import FastAPI, Request


app = FastAPI()


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data["query"]
    if query:
        url = make_url(query)
        elements = google_search(url)
        results = clean_data(elements, with_links=False)
        return {"results": results}
    else:
        return {"error": "No query provided"}
