from fake_useragent import UserAgent
from summarize import summarize
from urllib.parse import quote
from bs4 import BeautifulSoup
import requests

trusted_domains = [
    "wikipedia.org",
    "kun.uz",
    "daryo.uz",
    "spot.uz",
    "qalampir.uz",
]

classes = {
    "V3FYCf": ["hgKElc", "featured_snippet"],
    "xGj8Mb": ["kno-rdesc", "description"],
}


def get_title(element) -> str:
    element = element.find("h3")
    return element.get_text(separator=" ", strip=True) if element else ""


def get_text(element, class_name) -> str:
    element = element.find("div", class_=class_name)
    return element.get_text(separator=" ", strip=True) if element else ""


def get_url(element) -> str:
    a = element.find("a")
    return a.get("href", "") if a else ""


def search(query: str, lang: str) -> str:
    url = f"https://www.google.com/search?hl={lang}&gl=uz&num=5&q={quote(query)}"
    response = requests.get(url, headers={"User-Agent": UserAgent().random})
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for class_name in classes:
        element = soup.find("div", class_=class_name)
        if element:
            results.append({
                "title": get_title(element),
                classes[class_name][1]: get_text(element, classes[class_name][0]),
                "url": get_url(element),
            })

    do_summary = True
    element = soup.find("div", class_="MjjYud")
    if element:
        if not element.find("div", class_="VwiC3b"):
            results.append({
                "title": get_title(element),
                "result": element.get_text(separator=" ", strip=True),
                "url": get_url(element),
            })
            do_summary = False
        for element in soup.find_all("div", class_="MjjYud"):
            results.append({
                "title": get_title(element),
                "result": get_text(element, "VwiC3b"),
                "url": get_url(element),
            })

    i = 0
    while i < len(results):
        if (not results[i].get("featured_snippet", "") and
                not results[i].get("description", "") and not results[i].get("result", "")):
            results.pop(i)
        else:
            if do_summary and any(domain in results[i]["url"] for domain in trusted_domains):
                return summarize(query, results[i]["url"], num_sentences=10)
            if not results[i]["title"]:
                results[i].pop("title")
            if not results[i]["url"]:
                results[i].pop("url")
            i += 1

    response = ""
    for result in results:
        for key in result:
            response += f"{key}: {result[key]}\n"
        response += "\n"
    return response
