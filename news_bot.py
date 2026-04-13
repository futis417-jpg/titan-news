import requests
from bs4 import BeautifulSoup
import os
import random
import time
from datetime import datetime

# ==============================================================================
# ⚙️ 1. CONFIGURACIÓN DEL IMPERIO (SECRETOS GITHUB)
# ==============================================================================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# TÍTULO DEL BOTÓN
TEXTO_BOTON = "🔗 LEER ARTÍCULO COMPLETO"

# LISTA DE CATEGORÍAS Y TEMAS (SELECCIÓN ALEATORIA)
CATEGORIAS = {
    "Deportes": "https://news.google.com/rss/search?q=deportes+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Fútbol": "https://news.google.com/rss/search?q=futbol+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Fórmula 1": "https://news.google.com/rss/search?q=f1+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Bolsa de Valores": "https://news.google.com/rss/search?q=bolsa+española+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Tecnología": "https://news.google.com/rss/search?q=tecnologia+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Inteligencia Artificial": "https://news.google.com/rss/search?q=ia+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Mercado Inmobiliario": "https://news.google.com/rss/search?q=vivienda+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
    "Criptomonedas": "https://news.google.com/rss/search?q=cripto+when:1h&hl=es-ES&gl=ES&ceid=ES:es"
}

# ==============================================================================
# 🕵️‍♂️ 2. MOTOR DE SCRAPING CON CAPTURA DE IMAGEN
# ==============================================================================
def obtener_noticia_completa():
    # Elegimos una categoría al azar
    categoria, url_rss = random.choice(list(CATEGORIAS.items()))
    print(f"🔍 Buscando noticia de la categoría: {categoria.upper()}")
    
    try:
        # 1. Leer RSS
        response = requests.get(url_rss, timeout=15)
        soup_rss = BeautifulSoup(response.content, features="xml")
        items = soup_rss.find_all('item')
        
        if items:
            # Seleccionamos la más reciente
            noticia = {
                "titulo": items[0].title.text,
                "link": items[0].link.text,
                "id": items[0].guid.text,
                "categoria": categoria.upper(),
                "imagen": None
            }
            
            # 2. Scrapear la web original para buscar la imagen principal
            try:
                # Obtenemos la URL original (Google RSS a veces la encripta)
                response_web = requests.get(noticia["link"], timeout=10)
                soup_web = BeautifulSoup(response_web.content, 'html.parser')
                
                # Buscamos la imagen principal usando OpenGraph o Twitter Card
                meta_imagen = soup_web.find('meta', property='og:image') or \
                              soup_web.find('meta', attrs={'name': 'twitter:image'})
                
                if meta_imagen:
                    noticia["imagen"] = meta_imagen.get('content')
                    print("✅ Imagen capturada con éxito.")
                else:
                    print("📭 Imagen principal no encontrada en la web original.")
                    
            except Exception as e:
                print(f"⚠️ Error capturando imagen: {e}")
                
            return noticia
            
    except Exception as e:
        print(f"❌ Error en el scraper RSS: {e}")
    return None

# ==============================================================================
# 🎮 3. MOTOR DE PUBLICACIÓN (FORMATO PREMIUM CON IMAGEN Y BOTÓN)
# ==============================================================================
def enviar_a_telegram(noticia):
    # Definimos el formato visual del mensaje
    mensaje = (
        f"🔥 *ÚLTIMA HORA | {noticia['categoria']}*\n\n"
        f"📌 `{noticia['titulo']}`\n\n"
        f"🤖 _Enviado automáticamente por Titán News Bot_"
    )
    
    # Preparamos el botón (Inline Keyboard)
    # IMPORTANTE: Aquí estaba el error. Usamos 'teclado' en todo el proceso.
    teclado = {
        "inline_keyboard": [
            [
                {"text": TEXTO_BOTON, "url": noticia["link"]}
            ]
        ]
    }
    
    # Si tenemos imagen, enviamos como foto con pie de foto
    if noticia["imagen"]:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": noticia["imagen"],
            "caption": mensaje,
            "parse_mode": "Markdown",
            "reply_markup": teclado # Corregido: keyboard -> teclado
        }
    else:
        # Si no hay imagen, enviamos solo texto con vista previa desactivada (opcional)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": mensaje,
            "parse_mode": "Markdown",
            "reply_markup": teclado, # Corregido: keyboard -> teclado
            "disable_web_page_preview": False
        }
    
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Fallo al enviar a Telegram: {e}")

# ==============================================================================
# 🚀 4. INICIADOR PRINCIPAL CON MEMORIA
# ==============================================================================
if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("❌ Faltan los Secretos en GitHub (TELEGRAM_TOKEN o CHANNEL_ID)")
        exit(1)

    info_noticia = obtener_noticia_completa()
    
    if info_noticia:
        archivo_memoria = "last_news_id.txt"
        last_id = ""
        
        if os.path.exists(archivo_memoria):
            with open(archivo_memoria, "r") as f:
                last_id = f.read().strip()

        if info_noticia["id"] != last_id:
            enviar_a_telegram(info_noticia)
            with open(archivo_memoria, "w") as f:
                f.write(info_noticia["id"])
            print(f"✅ ¡Noticia publicada con éxito!: {info_noticia['titulo']}")
        else:
            print("😴 Esta noticia ya la hemos publicado. No se repite para evitar spam.")
    else:
        print("📭 No se han encontrado noticias nuevas en este momento.")
