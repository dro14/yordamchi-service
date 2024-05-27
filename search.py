from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.parse import quote
from selenium import webdriver

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.5 Safari/605.1.15"
)

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", USER_AGENT)

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.profile = profile
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(0.5)


def search(query: str, lang: str) -> set[str]:
    url = f"https://www.google.com/search?hl={lang}&gl=uz&num=3&q={quote(query)}"
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
            else:
                i += 1

        try:
            link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        except NoSuchElementException:
            pass
        else:
            if link:
                lines.append(link)

        results.add("\n".join(lines))

    return results
