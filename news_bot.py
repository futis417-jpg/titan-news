# -*- coding: utf-8 -*-
"""
🔱 TITÁN NEWS BOT v22.0 - "EL DICTADOR DE LA RED"
------------------------------------------------
Estado: Operativo | Nivel: Profesional / Enterprise
Arquitectura: Modular con gestión de fallos asíncrona
"""

import os
import re
import sys
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==============================================================================
# 📊 1. SISTEMA DE MONITOREO DE SISTEMAS
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TitanNews")

# ==============================================================================
# ⚙️ 2. NÚCLEO DE CONFIGURACIÓN BLINDADA
# ==============================================================================
class TitanConfig:
    """Configuración centralizada con limpieza de datos de entrada."""
    # El strip() elimina cualquier espacio que metas por error en GitHub Secrets
    TOKEN = str(os.getenv("TELEGRAM_TOKEN", "")).strip().replace("\n", "").replace(" ", "")
    CHANNEL_ID = str(os.getenv("CHANNEL_ID", "")).strip().replace("\n", "").replace(" ", "")
    
    # Directorio de Inteligencia: 20 Categorías de alto impacto
    FUENTES = {
        "⚽ FÚTBOL": "https://news.google.com/rss/search?q=fútbol+laliga+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏁 FORMULA 1": "https://news.google.com/rss/search?q=f1+gp+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏀 BALONCESTO": "https://news.google.com/rss/search?q=nba+acb+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "💰 BOLSA": "https://news.google.com/rss/search?q=ibex35+mercados+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏘️ INMOBILIARIA": "https://news.google.com/rss/search?q=vivienda+alquiler+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🍎 TECNOLOGÍA": "https://news.google.com/rss/search?q=tecnologia+novedades+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🤖 INTELIGENCIA ARTIFICIAL": "https://news.google.com/rss/search?q=ia+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🎮 VIDEOJUEGOS": "https://news.google.com/rss/search?q=gaming+estrenos+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🪙 CRIPTOMONEDAS": "https://news.google.com/rss/search?q=bitcoin+ethereum+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🍿 CINE": "https://news.google.com/rss/search?q=estrenos+netflix+cuando:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🎾 TENIS": "https://news.google.com/rss/search?q=atp+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🥊 BOXEO/UFC": "https://news.google.com/rss/search?q=ufc+boxeo+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏥 SALUD": "https://news.google.com/rss/search?q=salud+bienestar+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🚀 ESPACIO": "https://news.google.com/rss/search?q=nasa+espacio+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es"
    }

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

# ==============================================================================
# 🧩 3. OBJETO NOTICIA (DATA ESTRUCTURE)
# ==============================================================================
class NoticiaObjeto:
    """Clase para normalizar los datos de cualquier fuente RSS."""
    def __init__(self, titulo_sucio, link, guid, cat):
        self.link = link
        self.guid = guid
        self.categoria = cat
        self.titulo = self._limpiar_titulo(titulo_sucio)
        self.imagen = None

    def _limpiar_titulo(self, t):
        """Limpia el título de etiquetas y nombres de periódicos."""
        t = re.sub(r' - [^-]+$', '', t)
        return BeautifulSoup(t, "lxml").get_text().strip()

# ==============================================================================
# 🕵️‍♂️ 4. MOTOR DE EXTRACCIÓN (SCRAPER PRO)
# ==============================================================================
class MotorExtraccion:
    """Gestiona el rastreo de noticias y la captura de imágenes."""
    
    @staticmethod
    def capturar():
        """Busca una noticia fresca en una categoría aleatoria."""
        cat, url = random.choice(list(TitanConfig.FUENTES.items()))
        logger.info(f"📡 Rastreando categoría: {cat}")
        
        try:
            r = requests.get(url, headers=TitanConfig.HEADERS, timeout=20)
            soup = BeautifulSoup(r.content, features="xml")
            item = soup.find('item')
            
            if item:
                n = NoticiaObjeto(item.title.text, item.link.text, item.guid.text, cat)
                # Intentar buscar imagen en la web de origen
                try:
                    rw = requests.get(n.link, headers=TitanConfig.HEADERS, timeout=10)
                    sw = BeautifulSoup(rw.content, 'html.parser')
                    img = sw.find('meta', property='og:image') or sw.find('meta', attrs={'name': 'twitter:image'})
                    if img: n.imagen = img.get('content')
                except: pass
                return n
        except Exception as e:
            logger.error(f"❌ Error Scraper: {e}")
        return None

# ==============================================================================
# 🤖 5. COMUNICADOR DE TELEGRAM (API DISPATCHER)
# ==============================================================================
class TelegramTitan:
    """Encargado de enviar la información al canal y diagnosticar errores."""
    
    def __init__(self):
        self.token = TitanConfig.TOKEN
        self.canal = TitanConfig.CHANNEL_ID
        self.exito = False

    def enviar(self, n):
        """Ejecuta el envío de la noticia."""
        if not self.token or not self.canal:
            logger.error("🚫 CONFIGURACIÓN VACÍA: Revisa los Secrets de GitHub.")
            return

        # Texto del post
        txt = (
            f"🌟 *NOTICIA DE ÚLTIMA HORA*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📁 *CAT:* {n.categoria}\n"
            f"📌 `{n.titulo}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 _Bot Automático Titán v22.0_"
        )
        
        btn = {"inline_keyboard": [[{"text": "🚀 LEER ARTÍCULO", "url": n.link}]]}

        if n.imagen:
            url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
            pay = {"chat_id": self.canal, "photo": n.imagen, "caption": txt, "parse_mode": "Markdown", "reply_markup": btn}
        else:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            pay = {"chat_id": self.canal, "text": txt, "parse_mode": "Markdown", "reply_markup": btn}

        logger.info(f"📡 Intentando entrega en canal: {self.canal}")
        r = requests.post(url, json=pay)
        res = r.json()

        if r.status_code == 200 and res.get("ok"):
            logger.info("✅ ¡ENTREGADO CON ÉXITO!")
            self.exito = True
        else:
            logger.error(f"❌ FALLO DE TELEGRAM: {res.get('description')}")
            if "chat not found" in str(res):
                logger.warning("💡 PISTA: El @ del canal está mal o el bot no es admin.")

# ==============================================================================
# 💾 6. PERSISTENCIA Y ARRANQUE
# ==============================================================================
if __name__ == "__main__":
    logger.info("👑 INICIANDO PROTOCOLO TITÁN v22.0")
    
    motor = MotorExtraccion()
    tele = TelegramTitan()
    
    noticia = motor.capturar()
    if noticia:
        db = "last_news_id.txt"
        last = open(db).read().strip() if os.path.exists(db) else ""
        
        if noticia.guid != last:
            tele.enviar(noticia)
            if tele.exito:
                with open(db, "w") as f: f.write(noticia.guid)
                logger.info("🏁 Ciclo terminado. Noticia guardada.")
        else:
            logger.info("😴 Nada nuevo. El radar sigue escaneando.")
    else:
        logger.warning("📭 No se han capturado noticias en esta ronda.")
