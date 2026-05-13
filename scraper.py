import feedparser
import requests
import json
from bs4 import BeautifulSoup
from collections import defaultdict

RSS_FEEDS = [

    {
        "site": "BBC",
        "rss": "https://feeds.bbci.co.uk/portuguese/rss.xml"
    },

    {
        "site": "G1",
        "rss": "https://g1.globo.com/rss/g1/"
    },

    {
        "site": "UOL",
        "rss": "https://rss.uol.com.br/feed/noticias.xml"
    },

    {
        "site": "CNN Brasil",
        "rss": "https://www.cnnbrasil.com.br/feed/"
    },

    {
        "site": "Terra",
        "rss": "https://www.terra.com.br/rss.xml"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

articles = []


def get_image(url):

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        og = soup.find(
            "meta",
            property="og:image"
        )

        if og:
            return og.get("content", "")

    except:
        pass

    return ""


# coleta feeds
for source in RSS_FEEDS:

    print(f"Coletando {source['site']}")

    feed = feedparser.parse(source["rss"])

    for item in feed.entries[:10]:

        title = item.get("title", "")

        link = item.get("link", "")

        image = ""

        # tenta pegar imagem do RSS
        if "media_content" in item:

            try:
                image = item.media_content[0]["url"]
            except:
                pass

        # fallback
        if not image:
            image = get_image(link)

        article = {

            "site": source["site"],
            "title": title,
            "url": link,
            "image": image
        }

        articles.append(article)

        print("✔", title)


# remove duplicados
unique = []

links = set()

for article in articles:

    if article["url"] in links:
        continue

    links.add(article["url"])

    unique.append(article)


# separa por site
grouped = defaultdict(list)

for article in unique:

    grouped[article["site"]].append(article)


# mistura notícias
mixed = []

while True:

    added = False

    for site in grouped:

        if grouped[site]:

            mixed.append(
                grouped[site].pop(0)
            )

            added = True

    if not added:
        break


# salva
with open(
    "articles.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mixed,
        f,
        indent=2,
        ensure_ascii=False
    )

print("✔ Total:", len(mixed))
