import requests
from bs4 import BeautifulSoup
import sqlite3
import re


def obtener_pagina(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parsear_portada(html):
    soup = BeautifulSoup(html, "html.parser")
    articulos = []

    for item in soup.find_all("div", class_="body-post"):
        titulo = item.find("h2", class_="home-title")
        enlace = item.find("a", href=True)
        resumen = item.find("div", class_="home-desc")

        try:
            m = re.search(r'https?://[^/]+/(\d{4})/(\d{2})/', enlace["href"])
            anno, mes = m.group(1), m.group(2)
        except:
            anno, mes = "1970", "1"

        if titulo and enlace:
            articulos.append({
                "fecha": f"{anno}/{mes}",
                "titulo": titulo.get_text(strip=True),
                "url": enlace["href"],
                "resumen": resumen.get_text(strip=True) if resumen else ""
            })
    return articulos

def obtener_contenido(url):
    html = obtener_pagina(url)
    soup = BeautifulSoup(html, "html.parser")
    cuerpo = soup.find("div", class_="articlebody")
    return cuerpo.get_text(separator="\n", strip=True) if cuerpo else ""

def crear_tabla():
    conn = sqlite3.connect("hackernews.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articulos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        titulo TEXT,
        url TEXT UNIQUE,
        resumen TEXT,
        contenido TEXT
    )
    """)
    conn.commit()
    conn.close()

def guardar_articulo(conn, fecha, titulo, url, resumen, contenido):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO articulos (fecha, titulo, url, resumen, contenido)
    VALUES (?, ?, ?, ?, ?)
    """, (fecha, titulo, url, resumen, contenido))
    conn.commit()

def main():
    crear_tabla()
    conn = sqlite3.connect("hackernews.db")

    url_actual = "https://thehackernews.com/"
    paginas_recorridas = 0
    max_paginas = 3  # Número de páginas que queremos scrapear

    while url_actual and paginas_recorridas < max_paginas:
        html = obtener_pagina(url_actual)
        posts = parsear_portada(html)

        for a in posts:
            contenido = obtener_contenido(a["url"])
            guardar_articulo(conn, a["fecha"], a["titulo"], a["url"], a["resumen"], contenido)
            print("Guardado:", a["titulo"])

        # Buscar enlace a la siguiente página
        soup = BeautifulSoup(html, "html.parser")
        siguiente = soup.find("a", class_=["blog-pager-older-link", "blog-pager-older-link-mobile"])
        if siguiente and "href" in siguiente.attrs:
            url_actual = siguiente["href"]
        else:
            break

        paginas_recorridas += 1

    conn.close()

if __name__ == "__main__":
    main()
