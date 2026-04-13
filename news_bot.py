import requests
from bs4 import BeautifulSoup
import os
import random
import time
from datetime import datetime

# ==========================================
# ⚙️ 1. CONFIGURACIÓN (SECRETOS GITHUB)
# ==========================================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TEXTO_BOTON = "🔗 LEER NOTICIA COMPLETA"

# CATEGORÍAS MEJORADAS
CATEGORIAS = {
    "Deportes": "https://news.google.com/rss/search?q=deportes+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Fútbol": "https://news.google.com/rss/search?q=futbol+españa+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Fórmula 1": "https://news.google.com/rss/search?q=f1+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Bolsa y Finanzas": "https://news.google.com/rss/search?q=ibex35+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Tecnología": "https://news.google.com/rss/search?q=tecnologia+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Inteligencia Artificial": "https://news.google.com/rss/search?q=ia+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Mercado Inmobiliario": "https://news.google.com/rss/search?q=vivienda+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Criptomonedas": "https://news.google.com/rss/search?q=bitcoin+when:1h&hl=es-ES&gl=ES&ceid=ES:es"
}

# ==========================================
# 🕵️‍♂️ 2. EXTRACTOR DE NOTICIAS E IMÁGENES
# ==========================================
def obtener_noticia():
    cat, url_rss = random.choice(list(CATEGORIAS.items()))
    print(f"🔍 Explorando: {cat}")
    
    try:
        r = requests.get(url_rss, timeout=15)
        soup = BeautifulSoup(r.content, features="xml")
        item = soup.find('item')
        
        if item:
            data = {
                "titulo": item.title.text,
                "link": item.link.text,
                "id": item.guid.text,
                "categoria": cat.upper(),
                "imagen": None
            }
            
            # Intentar capturar imagen de la web original
            try:
                rw = requests.get(data["link"], timeout=10)
                sw = BeautifulSoup(rw.content, 'html.parser')
                img = sw.find('meta', property='og:image') or sw.find('meta', attrs={'name': 'twitter:image'})
                if img:
                    data["imagen"] = img.get('content')
            except:
                pass
            return data
    except Exception as e:
        print(f"❌ Error Scraper: {e}")
    return None

# ==========================================
# 🎮 3. ENVÍO A TELEGRAM
# ==========================================
def enviar_telegram(n):
    # Limpieza del Token por seguridad
    tkn = TOKEN.strip()
    
    mensaje = (
        f"🔥 *ÚLTIMA HORA | {n['categoria']}*\n\n"
        f"📌 `{n['titulo']}`\n\n"
        f"🤖 _Enviado por Titán News v18.5_"
    )
    
    markup = {"inline_keyboard": [[{"text": TEXTO_BOTON, "url": n["link"]}]]}
    
    if n["imagen"]:
        url = f"https://api.telegram.org/bot{tkn}/sendPhoto"
        pay = {"chat_id": CHANNEL_ID, "photo": n["imagen"], "caption": mensaje, "parse_mode": "Markdown", "reply_markup": markup}
    else:
        url = f"https://api.telegram.org/bot{tkn}/sendMessage"
        pay = {"chat_id": CHANNEL_ID, "text": mensaje, "parse_mode": "Markdown", "reply_markup": markup}
    
    requests.post(url, json=pay)

# ==========================================
# 🚀 4. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("❌ Faltan SECRETOS en GitHub.")
        exit(1)

    noticia = obtener_noticia()
    if noticia:
        db = "last_news_id.txt"
        old_id = open(db).read().strip() if os.path.exists(db) else ""
        
        if noticia["id"] != old_id:
            enviar_telegram(noticia)
            with open(db, "w") as f: f.write(noticia["id"])
            print(f"✅ Publicado: {noticia['titulo']}")
        else:
            print("😴 Sin noticias nuevas.")
