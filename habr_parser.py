import requests as rq
from bs4 import BeautifulSoup
from aiogram.utils.markdown import hlink

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def get_first_article(habr_url="https://habr.com"):
    habr_url = "https://habr.com"
    response = rq.get(habr_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # проверяем, зашли ли мы на сайт
    if response.status_code == 200:
        print("получаем информацию/ get_first_article()")
    else:
        print('error/get_first_article()')

    try:
        element = soup.find("a", attrs={"class": "tm-title__link"})
        first_article_title = element.text if element else "err"
        first_article_url = element.get("href") if element else "err"

        full_url = habr_url + first_article_url

        article_and_url = hlink(first_article_title, full_url)
        return article_and_url

    except Exception as e:
        return ""


flows = ("backend", "frontend", "admin", "information_security",
         "gamedev", "ai_and_ml", "design", "management", "marketing",
         "popsci", "develop")


def get_article_by_flow(flow):
    habr_flows_url = "https://habr.com/flows/"
    habr_url = "https://habr.com"
    flow_url = habr_flows_url + flow
    response = rq.get(flow_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # проверяем, зашли ли мы на сайт
    if response.status_code == 200:
        print("получаем информацию/ get_article_by_flow()")
    else:
        print('error/get_article_by_flow()')

    try:
        element = soup.find("a", attrs={"class": "tm-title__link"})
        first_article_title = element.text if element else "err"
        first_article_url = element.get("href") if element else "err"

        full_url = habr_url + first_article_url

        article_and_url = hlink(first_article_title, full_url)
        print(full_url)
        return article_and_url

    except Exception as e:
        return ""


get_article_by_flow("frontend")

if __name__ == "__main__":
    ...
