from pylatexenc.latex2text import LatexNodes2Text
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from search import search
import tracemalloc
import subprocess
import uvicorn
import sys

tracemalloc.start()
log_file = open("yordamchi-service.log", "w")
sys.stdout = log_file
sys.stderr = log_file

subprocess.Popen(
    ["python", "bot.py"],
    stdout=log_file,
    stderr=log_file,
)

ltx2txt = LatexNodes2Text(
    strict_latex_spaces={
        "between-macro-and-chars": False,
        "after-comment": True,
        "between-latex-constructs": True,
        "in-equations": True,
    },
    keep_braced_groups=True,
)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


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
        return {"success": True, "results": results}


@app.post("/latex2text")
async def latex2text(request: Request):
    data = await request.json()
    latex = data["latex"]
    text = []
    for ltx in latex:
        text.append(ltx2txt.latex_to_text(ltx))
    return {"text": text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
