import requests
from bs4 import BeautifulSoup
import sqlite3

def obtener_pagina(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parsear_portada(html):
    soup = BeautifulSoup(html, "html.parser")
    artículos = []

    for item in soup.find_all("div", class_="body-post"):
        titulo = item.find("h2", class_="home-title")
        enlace = item.find("a", href=True)
        resumen = item.find("div", class_="home-desc")

        if titulo and enlace:
            artículos.append({
                "titulo": titulo.get_text(strip=True),
                "url": enlace["href"],
                "resumen": resumen.get_text(strip=True) if resumen else ""
            })
    return artículos

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
        titulo TEXT,
        url TEXT UNIQUE,
        resumen TEXT,
        contenido TEXT
    )
    """)
    conn.commit()
    conn.close()

def guardar_articulo(conn, titulo, url, resumen, contenido):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO articulos (titulo, url, resumen, contenido)
    VALUES (?, ?, ?, ?)
    """, (titulo, url, resumen, contenido))
    conn.commit()

def main():
    crear_tabla()

    url = "https://thehackernews.com/"
    html = obtener_pagina(url)
    posts = parsear_portada(html)
    conn = sqlite3.connect("hackernews.db")

    for a in posts:
        contenido = obtener_contenido(a["url"])
        guardar_articulo(conn, a["titulo"], a["url"], a["resumen"], contenido)
        print("Guardado:", a["titulo"])
    
    conn.close()

if __name__ == "__main__":
    main()
