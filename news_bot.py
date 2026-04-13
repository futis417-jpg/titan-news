import requests
from bs4 import BeautifulSoup
import os
import sys

# CONFIGURACIÓN (GitHub Secrets)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") # Ejemplo: @MiCanalNoticias

def obtener_ultima_noticia():
    # Usaremos Google News RSS para noticias frescas y rápidas
    url = "https://news.google.com/rss/search?q=tecnologia+cuando:1h&hl=es-ES&gl=ES&ceid=ES:es"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('item')
        if items:
            # Cogemos la primera (la más reciente)
            noticia = {
                "titulo": items[0].title.text,
                "link": items[0].link.text,
                "id": items[0].guid.text
            }
            return noticia
    except Exception as e:
        print(f"Error buscando noticias: {e}")
    return None

def enviar_telegram(titulo, link):
    mensaje = f"🔔 *ÚLTIMA HORA*\n\n📌 {titulo}\n\n🔗 [Leer noticia completa]({link})"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 1. Buscar noticia
    nueva_noticia = obtener_ultima_noticia()
    
    if nueva_noticia:
        # 2. Comprobar si ya la publicamos (Memoria)
        if os.path.exists("last_news_id.txt"):
            with open("last_news_id.txt", "r") as f:
                last_id = f.read().strip()
        else:
            last_id = ""

        if nueva_noticia["id"] != last_id:
            # 3. Publicar y guardar nuevo ID
            enviar_telegram(nueva_noticia["titulo"], nueva_noticia["link"])
            with open("last_news_id.txt", "w") as f:
                f.write(nueva_noticia["id"])
            print(f"✅ Noticia publicada: {nueva_noticia['titulo']}")
        else:
            print("😴 No hay noticias nuevas desde la última revisión.")
    else:
        print("❌ No se pudo obtener noticias.")
