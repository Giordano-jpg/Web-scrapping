import requests
from bs4 import BeautifulSoup
import time

def obtener_pagina(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parsear_articulos(html):
    soup = BeautifulSoup(html, "html.parser")
    artículos = []
    # Aquí dependerá cómo estructura The Hacker News sus artículos:
    for item in soup.find_all("div", class_="body-post"):  # ejemplo de clase, no sé si es la real
        título_tag = item.find("h2")
        enlace_tag = item.find("a", href=True)
        resumen_tag = item.find("div", class_="post-body")  # ejemplo
        if título_tag and enlace_tag:
            artículo = {
                "título": título_tag.get_text(strip=True),
                "url": enlace_tag["href"],
                "resumen": resumen_tag.get_text(strip=True) if resumen_tag else None
            }
            artículos.append(artículo)
    return artículos

def main():
    url = "https://thehackernews.com/"
    html = obtener_pagina(url)
    artículos = parsear_articulos(html)
    for a in artículos:
        print(a["título"])
        print(a["url"])
        print(a["resumen"])
        print("-" * 80)
        time.sleep(1)  # para no hacer peticiones muy rápidas

if __name__ == "__main__":
    main()
