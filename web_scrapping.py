from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://thehackernews.com/")

# Esperar a que cargue el contenido
driver.implicitly_wait(5)

# Obtener HTML renderizado
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Extraer titulares y enlaces
articles = soup.find_all("div", class_="body-post")
for article in articles:
    title_tag = article.find("h2", class_="home-title")
    link_tag = article.find("a", href=True)
    if title_tag and link_tag:
        print("Título:", title_tag.text.strip())
        print("Enlace:", link_tag["href"])
        print("-" * 50)

driver.quit()
