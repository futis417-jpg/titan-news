# -*- coding: utf-8 -*-
"""
🔱 TITÁN OMNIPRESENCIA v25.0 - THE IMPERIAL EDITION
--------------------------------------------------
Arquitectura: Multi-threaded Categorical Scraper
Capacidad: Extracción de texto completo (Full Article)
Propósito: Dominio absoluto de información en Telegram
"""

import os
import re
import sys
import time
import json
import random
import logging
import traceback
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# 📊 1. SISTEMA DE LOGS NIVEL INDUSTRIAL
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN-OMNI] - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OmniBot")

# ==============================================================================
# ⚙️ 2. CONFIGURACIÓN MAESTRA DE CATEGORÍAS Y SEGURIDAD
# ==============================================================================
class Config:
    TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip().replace("\n", "").replace(" ", "")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip().replace("\n", "").replace(" ", "")
    
    # 🌍 Diccionario Global de Fuentes (Sección: Guerras, Deportes, Tech, etc.)
    FUENTES = {
        "🪖 CONFLICTOS Y GUERRAS": "https://news.google.com/rss/search?q=guerra+conflictos+internacional+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "⚽ FÚTBOL MUNDIAL": "https://news.google.com/rss/search?q=fútbol+fichajes+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "💰 ECONOMÍA Y BOLSA": "https://news.google.com/rss/search?q=ibex35+economía+finanzas+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏘️ MERCADO INMOBILIARIO": "https://news.google.com/rss/search?q=vivienda+precio+alquiler+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🤖 TECNOLOGÍA E IA": "https://news.google.com/rss/search?q=ia+tecnología+novedades+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏎️ MOTOR Y F1": "https://news.google.com/rss/search?q=f1+motogp+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🧬 CIENCIA Y SALUD": "https://news.google.com/rss/search?q=ciencia+descubrimientos+salud+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🪙 CRIPTOMONEDAS": "https://news.google.com/rss/search?q=bitcoin+cripto+mercado+when:1h&hl=es-ES&gl=ES&ceid=ES:es"
    }

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

# ==============================================================================
# 🧩 3. MODELO DE DATOS AVANZADO
# ==============================================================================
class ArticuloImperial:
    def __init__(self, titulo, link, guid, categoria):
        self.titulo = self._limpiar(titulo)
        self.link = link
        self.guid = guid
        self.categoria = categoria
        self.cuerpo = ""
        self.imagen = None
        self.timestamp = datetime.now().strftime("%H:%M:%S")

    def _limpiar(self, texto):
        texto = re.sub(r' - [^-]+$', '', texto) # Quitar fuente al final
        return texto.strip()

# ==============================================================================
# 🧠 4. MOTOR DE EXTRACCIÓN DE CONTENIDO (FULL TEXT SCRAPER)
# ==============================================================================
class ContentExtractor:
    """Extrae el texto completo de las noticias para lectura en Telegram."""
    
    @staticmethod
    def extraer_todo(articulo):
        logger.info(f"🧪 Extrayendo contenido completo: {articulo.titulo[:40]}...")
        try:
            r = requests.get(articulo.link, headers=Config.HEADERS, timeout=15)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # 1. Buscar imagen principal
            img_tag = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'twitter:image'})
            if img_tag:
                articulo.imagen = img_tag.get('content')

            # 2. Extraer párrafos de texto (Lógica de limpieza)
            parrafos = soup.find_all('p')
            texto_acumulado = []
            
            for p in parrafos:
                txt = p.get_text().strip()
                # Filtrar párrafos cortos o basura de cookies/publicidad
                if len(txt) > 60 and not any(x in txt.lower() for x in ['cookies', 'suscríbete', 'clic aquí']):
                    texto_acumulado.append(txt)
                
                # No saturar Telegram (Máximo 10 párrafos para legibilidad)
                if len(texto_acumulado) >= 8:
                    break
            
            if texto_acumulado:
                articulo.cuerpo = "\n\n".join(texto_acumulado)
            else:
                articulo.cuerpo = "_(No se ha podido extraer el resumen completo de este medio, por favor revise la fuente original si desea más detalles)_"
                
        except Exception as e:
            logger.error(f"⚠️ Error extrayendo contenido de {articulo.link}: {e}")
            articulo.cuerpo = "_(Error de conexión con la fuente original)_"
        
        return articulo

# ==============================================================================
# 🤖 5. DESPACHADOR IMPERIAL DE TELEGRAM
# ==============================================================================
class TelegramImperial:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{Config.TOKEN}"

    def publicar(self, n):
        logger.info(f"📡 Publicando en canal: {Config.CHANNEL_ID}")
        
        # Construcción de la Noticia Completa
        mensaje = (
            f"👑 *TITÁN INFORMA | {n.categoria}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📌 *{n.titulo}*\n\n"
            f"{n.cuerpo}\n\n"
            f"🕒 _Hora: {n.timestamp}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔗 [Link a la fuente original]({n.link})"
        )

        # Truncar mensaje si excede el límite de Telegram (4096 caracteres)
        if len(mensaje) > 4000:
            mensaje = mensaje[:3900] + "...\n\n_(Noticia demasiado larga para mostrarla completa en Telegram)_"

        payload = {
            "chat_id": Config.CHANNEL_ID,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

        if n.imagen:
            endpoint = f"{self.url}/sendPhoto"
            payload["photo"] = n.imagen
            payload["caption"] = mensaje
        else:
            endpoint = f"{self.url}/sendMessage"
            payload["text"] = mensaje

        try:
            r = requests.post(endpoint, json=payload, timeout=25)
            res = r.json()
            if not res.get("ok"):
                logger.error(f"❌ Fallo Telegram: {res.get('description')}")
                return False
            return True
        except Exception as e:
            logger.error(f"💥 Error conexión Telegram: {e}")
            return False

# ==============================================================================
# 💾 6. GESTIÓN DE PERSISTENCIA POR CATEGORÍA
# ==============================================================================
class DatabaseVault:
    FILE_NAME = "titan_history.json"

    @classmethod
    def leer_historial(cls):
        if os.path.exists(cls.FILE_NAME):
            try:
                with open(cls.FILE_NAME, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @classmethod
    def guardar_id(cls, categoria, guid):
        data = cls.leer_historial()
        data[categoria] = guid
        with open(cls.FILE_NAME, "w") as f:
            json.dump(data, f)

# ==============================================================================
# 🚀 7. ORQUESTADOR MAESTRO (PARALLEL EXECUTION)
# ==============================================================================
def procesar_categoria(nombre_cat, url_rss, historial, telegram):
    """Procesa una categoría individual de principio a fin."""
    try:
        r = requests.get(url_rss, headers=Config.HEADERS, timeout=20)
        soup = BeautifulSoup(r.content, features="xml")
        item = soup.find('item')
        
        if not item:
            return

        guid = item.guid.text
        if historial.get(nombre_cat) == guid:
            logger.info(f"😴 {nombre_cat}: Sin novedades.")
            return

        # Es nueva: Procesar
        articulo = ArticuloImperial(item.title.text, item.link.text, guid, nombre_cat)
        articulo = ContentExtractor.extraer_todo(articulo)
        
        # Publicar
        if telegram.publicar(articulo):
            DatabaseVault.guardar_id(nombre_cat, guid)
            logger.info(f"✅ {nombre_cat}: Publicada con éxito.")
            
    except Exception as e:
        logger.error(f"🔥 Error procesando categoría {nombre_cat}: {e}")

def ejecutar_imperio():
    logger.info("🔥 INICIANDO DESPLIEGUE OMNIPRESENTE TITÁN v25.0")
    
    telegram = TelegramImperial()
    historial = DatabaseVault.leer_historial()
    
    # Ejecutar todas las categorías en paralelo para máxima velocidad
    with ThreadPoolExecutor(max_workers=5) as executor:
        for nombre, url in Config.FUENTES.items():
            executor.submit(procesar_categoria, nombre, url, historial, telegram)
            time.sleep(2) # Pequeño delay para no saturar la API de Telegram

if __name__ == "__main__":
    inicio = time.time()
    try:
        ejecutar_imperio()
    except Exception:
        logger.critical(f"💀 FALLO SISTÉMICO:\n{traceback.format_exc()}")
    
    logger.info(f"⏱️ Operación finalizada en {round(time.time() - inicio, 2)}s.")
