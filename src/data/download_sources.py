import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

def search_ddg(query):
    print(f"Searching DuckDuckGo for: {query}")
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    r = requests.post(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    for el in soup.find_all('div', class_='result'):
        title_tag = el.find('a', class_='result__title')
        snippet_tag = el.find('a', class_='result__snippet')
        if title_tag:
            title = title_tag.text.strip()
            href = title_tag.get('href', '')
            if 'uddg=' in href:
                href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
            snippet = snippet_tag.text.strip() if snippet_tag else ''
            results.append({'title': title, 'url': href, 'snippet': snippet})
    return results

if __name__ == '__main__':
    res = search_ddg('site:anaao.it "pletora medica"')
    for r in res[:10]:
        print(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet'][:150]}\n")
