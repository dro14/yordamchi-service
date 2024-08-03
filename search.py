from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
from summarize import summarize
from selenium import webdriver
from urllib.parse import quote

domains = [
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

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", UserAgent().random)

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.profile = profile
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(0.5)


def get_title(element) -> str:
    if element:
        try:
            return element.find_element("css selector", "h3").text
        except NoSuchElementException:
            pass
    return ""


def get_text(element, class_name) -> str:
    if element and class_name:
        try:
            return element.find_element("class name", class_name).text
        except NoSuchElementException:
            pass
    return ""


def get_url(element) -> str:
    if element:
        try:
            return element.find_element("css selector", "a").get_attribute("href")
        except NoSuchElementException:
            pass
    return ""


def search(query: str, lang: str) -> str:
    url = f"https://www.google.com/search?hl={lang}&gl=uz&num=5&q={quote(query)}"
    driver.get(url)

    try:
        driver.find_element("id", "L2AGLb").click()
    except NoSuchElementException:
        pass

    results = []
    for class_name in classes:
        try:
            element = driver.find_element("class name", class_name)
        except NoSuchElementException:
            continue
        else:
            results.append({
                "title": get_title(element),
                classes[class_name][1]: get_text(element, classes[class_name][0]),
                "url": get_url(element),
            })

    try:
        first_result = driver.find_element("class name", "MjjYud")
    except NoSuchElementException:
        pass
    else:
        results.append({
            "title": get_title(first_result),
            "result": first_result.text,
            "url": get_url(first_result),
        })
        for element in driver.find_elements("class name", "MjjYud"):
            results.append({
                "title": get_title(element),
                "result": get_text(element, "VwiC3b"),
                "url": get_url(element),
            })
            if results[-1]["url"] == get_url(first_result):
                results.pop()

    i = 0
    while i < len(results):
        if (not results[i].get("featured_snippet", "") and
                not results[i].get("description", "") and not results[i].get("result", "")):
            results.pop(i)
        else:
            if any(domain in results[i]["url"] for domain in domains):
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

