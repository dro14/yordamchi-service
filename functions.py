from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from urllib.parse import quote
from re import match

REDUNDANT_LINES = (
    r"http",
    r"·",
    r"Translate this page",
    r"•",
    r"Feedback",
    r"Missing",
    r"Rating",
    r"\d+ answers",
    r"Top answer:",
    r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s([1-9]|[12][0-9]|3[01]),\s\d{4}$",
)

options = FirefoxOptions()
options.add_argument("--headless")
driver = Firefox(options=options)
driver.implicitly_wait(1)


def make_url(query):
    return "https://www.google.com/search?hl=en&gl=uz&num=10&q=" + quote(query)


def google_search(url):
    driver.get(url)

    try:
        driver.find_element(By.ID, "L2AGLb").click()
    except NoSuchElementException:
        pass

    elements = []
    try:
        elements.extend(driver.find_elements(By.CLASS_NAME, "Kot7x"))
    except NoSuchElementException:
        pass
    try:
        elements.extend(driver.find_elements(By.CLASS_NAME, "MjjYud"))
    except NoSuchElementException:
        pass

    return elements


def clean_data(elements, with_links=True):
    results = []
    for element in elements:
        redundant_elements = ("People also ask", "Related searches", "Related search", "Images", "Videos")
        if not element.text or element.text.startswith(redundant_elements):
            continue

        lines = element.text.splitlines()

        i = 0
        while i < len(lines):
            lines[i] = lines[i].strip()
            for redundant_line in REDUNDANT_LINES:
                if match(redundant_line, lines[i]):
                    lines.pop(i)
                    i -= 1
                    break
            i += 1

        if with_links:
            try:
                link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except NoSuchElementException:
                link = None

            if link:
                lines.append(link)

        results.append("\n".join(lines))

    return "\n\n".join(results)
