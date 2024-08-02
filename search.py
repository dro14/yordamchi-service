from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from urllib.parse import quote
import json

classes = {
    "V3FYCf": ["hgKElc", "featured_snippet"],
    "xGj8Mb": ["kno-rdesc", "description"],
}

user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.5 Safari/605.1.15"
)

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", user_agent)

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.profile = profile
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(0.5)


def get_title(element) -> str:
    try:
        return element.find_element("css selector", "h3").text
    except NoSuchElementException:
        return ""


def get_text(element, class_name) -> str:
    try:
        return element.find_element("class name", class_name).text
    except NoSuchElementException:
        return ""


def get_url(element) -> str:
    try:
        return element.find_element("css selector", "a").get_attribute("href")
    except NoSuchElementException:
        return ""


def search(query: str, lang: str) -> str:
    url = f"https://www.google.com/search?hl={lang}&gl=uz&num=3&q={quote(query)}"
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
        results.append({
            "title": get_title(element),
            classes[class_name][1]: get_text(element, classes[class_name][0]),
            "url": get_url(element),
        })

    first_result = driver.find_element("class name", "MjjYud")
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
            if not results[i]["title"]:
                results[i].pop("title")
            if not results[i]["url"]:
                results[i].pop("url")
            i += 1

    return json.dumps(results, ensure_ascii=False, indent=4)
