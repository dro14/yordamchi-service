from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from urllib.parse import quote

options = FirefoxOptions()
options.add_argument("--headless")
driver = Firefox(options=options)
driver.implicitly_wait(1)


def make_url(lang, query):
    return f"https://www.google.com/search?hl={lang}&gl=uz&num=10&q=" + quote(query)


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
    results = set()
    for element in elements:
        if not element.text.strip():
            continue

        lines = element.text.splitlines()

        i = 0
        while i < len(lines):
            lines[i] = lines[i].strip()
            if lines[i].startswith(("http", "·", "•")):
                lines.pop(i)
                i -= 1
            i += 1

        if with_links:
            try:
                link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except NoSuchElementException:
                link = None

            if link:
                lines.append(link)

        results.add("\n".join(lines))

    return results
