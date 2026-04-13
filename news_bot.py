# -*- coding: utf-8 -*-
"""
🚀 TITÁN NEWS BOT v20.0 - "MEGALODÓN IMPERIAL"
Arquitectura: Programación Orientada a Objetos (POO)
Propósito: Automatización masiva de noticias con IA y Scraping avanzado.
Alojamiento: GitHub Actions (Serverless Engine)
"""

import os
import re
import sys
import time
import random
import logging
import traceback
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==============================================================================
# 🛠️ CONFIGURACIÓN DE LOGGING (EL ESPEJO DEL ALMA DEL BOT)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN-LOG] - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# ⚙️ CLASE DE CONFIGURACIÓN Y CONSTANTES
# ==============================================================================
class Config:
    """Gestiona todas las variables de entorno y constantes del sistema."""
    TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
    CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
    
    # Lista Maestra de Categorías (El motor de variedad del canal)
    CATEGORIAS = {
        "⚽ DEPORTES": "https://news.google.com/rss/search?q=deportes+españa+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏟️ FÚTBOL": "https://news.google.com/rss/search?q=fútbol+laliga+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏎️ FÓRMULA 1": "https://news.google.com/rss/search?q=f1+noticias+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏀 BALONCESTO": "https://news.google.com/rss/search?q=nba+acb+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "💰 ECONOMÍA": "https://news.google.com/rss/search?q=economía+finanzas+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "📈 BOLSA": "https://news.google.com/rss/search?q=ibex35+mercados+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🏠 VIVIENDA": "https://news.google.com/rss/search?q=vivienda+alquiler+españa+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "💻 TECNOLOGÍA": "https://news.google.com/rss/search?q=tecnología+gadgets+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🤖 INTELIGENCIA ARTIFICIAL": "https://news.google.com/rss/search?q=ia+inteligencia+artificial+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🎮 VIDEOJUEGOS": "https://news.google.com/rss/search?q=videojuegos+gaming+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🎬 CINE Y SERIES": "https://news.google.com/rss/search?q=netflix+estrenos+cine+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🧬 CIENCIA": "https://news.google.com/rss/search?q=ciencia+descubrimientos+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "₿ CRIPTOMONEDAS": "https://news.google.com/rss/search?q=bitcoin+ethereum+when:1h&hl=es-ES&gl=ES&ceid=ES:es",
        "🍎 SALUD": "https://news.google.com/rss/search?q=salud+bienestar+when:1h&hl=es-ES&gl=ES&ceid=ES:es"
    }

    # Blacklist de palabras para filtrar noticias basura
    BLACKLIST = ["oferta", "descuento", "cupón", "sexo", "casino", "apuestas", "vende"]
    
    # Cabeceras para evitar bloqueos de los servidores de noticias
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

# ==============================================================================
# 🧩 MODELO DE DATOS: NOTICIA
# ==============================================================================
class Noticia:
    """Estructura de datos para representar una noticia procesada."""
    def __init__(self, titulo, link, guid, categoria):
        self.titulo = self._limpiar_texto(titulo)
        self.link = link
        self.guid = guid
        self.categoria = categoria
        self.imagen = None
        self.fuente = "Google News"

    def _limpiar_texto(self, texto):
        """Elimina basura típica de los títulos de RSS."""
        # Quitar el nombre del medio al final (ej: "Título - El País")
        texto = re.sub(r' - [^-]+$', '', texto)
        # Quitar etiquetas HTML si las hubiera
        texto = BeautifulSoup(texto, "lxml").text
        return texto.strip()

# ==============================================================================
# 📡 MOTOR DE SCRAPING: EL EXPLORADOR
# ==============================================================================
class ScraperEngine:
    """Clase encargada de navegar por la web y extraer la información."""
    
    @staticmethod
    def obtener_rss_data():
        """Elige una categoría y extrae la noticia más reciente."""
        categoria, url = random.choice(list(Config.CATEGORIAS.items()))
        logger.info(f"🔎 Iniciando exploración en categoría: {categoria}")
        
        try:
            response = requests.get(url, headers=Config.HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, features="xml")
            
            items = soup.find_all('item')
            if not items:
                logger.warning(f"📭 No se encontraron noticias en {categoria}")
                return None
            
            # Buscamos la primera que no esté en la blacklist
            for item in items:
                titulo = item.title.text
                if any(palabra in titulo.lower() for palabra in Config.BLACKLIST):
                    continue
                
                return Noticia(
                    titulo=titulo,
                    link=item.link.text,
                    guid=item.guid.text,
                    categoria=categoria
                )
        except Exception as e:
            logger.error(f"❌ Error crítico en ScraperEngine: {e}")
        return None

    @staticmethod
    def capturar_imagen_principal(noticia):
        """Visita la noticia original para extraer la imagen destacada."""
        logger.info(f"📸 Intentando capturar imagen para: {noticia.titulo[:30]}...")
        try:
            r = requests.get(noticia.link, headers=Config.HEADERS, timeout=15)
            # A veces hay redirecciones de Google, las seguimos
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Estrategia de búsqueda de imagen (Prioridad: OpenGraph -> Twitter -> IMG)
            img_url = None
            
            # 1. OpenGraph
            og_img = soup.find('meta', property='og:image')
            if og_img:
                img_url = og_img.get('content')
            
            # 2. Twitter Card
            if not img_url:
                tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
                if tw_img:
                    img_url = tw_img.get('content')
            
            # 3. Primera imagen grande de la página (Fallback agresivo)
            if not img_url:
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if 'http' in src and any(ext in src for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        # Evitar iconos pequeños
                        if 'icon' not in src.lower() and 'logo' not in src.lower():
                            img_url = src
                            break
            
            if img_url:
                # Validar que la URL de la imagen sea completa
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                noticia.imagen = img_url
                logger.info(f"✅ Imagen encontrada: {img_url[:50]}...")
            else:
                logger.warning("📭 No se pudo encontrar una imagen válida.")
                
        except Exception as e:
            logger.warning(f"⚠️ Error al scrapear la web original para imagen: {e}")
        return noticia

# ==============================================================================
# 🤖 COMUNICADOR DE TELEGRAM: EL PORTAVOZ
# ==============================================================================
class TelegramDispatcher:
    """Clase encargada de hablar con la API de Telegram y gestionar errores."""
    
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{Config.TOKEN}"
        self.diagnostico_exitoso = False

    def enviar_mensaje(self, noticia):
        """Decide si enviar foto o texto y procesa la respuesta de Telegram."""
        if not Config.TOKEN or not Config.CHANNEL_ID:
            logger.error("🚫 Configuración incompleta: Falta TOKEN o CHANNEL_ID")
            return

        # Construcción del diseño del mensaje
        caption = (
            f"🔥 *ÚLTIMA HORA | {noticia.categoria}*\n\n"
            f"📌 `{noticia.titulo}`\n\n"
            f"🗞️ _Vía: {noticia.fuente}_\n"
            f"📅 _Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}_"
        )

        # Botón de lectura
        markup = {
            "inline_keyboard": [[
                {"text": "🚀 LEER NOTICIA COMPLETA", "url": noticia.link}
            ]]
        }

        # Intentar enviar con foto si existe
        if noticia.imagen:
            endpoint = f"{self.base_url}/sendPhoto"
            payload = {
                "chat_id": Config.CHANNEL_ID,
                "photo": noticia.imagen,
                "caption": caption,
                "parse_mode": "Markdown",
                "reply_markup": markup
            }
        else:
            endpoint = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": Config.CHANNEL_ID,
                "text": caption,
                "parse_mode": "Markdown",
                "reply_markup": markup,
                "disable_web_page_preview": False
            }

        try:
            response = requests.post(endpoint, json=payload, timeout=20)
            data = response.json()
            
            if response.status_code == 200 and data.get("ok"):
                logger.info("✅ MENSAJE ENTREGADO CORRECTAMENTE A TELEGRAM.")
                self.diagnostico_exitoso = True
            else:
                logger.error(f"❌ TELEGRAM RECHAZÓ EL MENSAJE: {data.get('description')}")
                # Si falla la foto, reintentar solo con texto por si la URL de imagen estaba rota
                if noticia.imagen:
                    logger.info("🔄 Reintentando envío sin imagen...")
                    noticia.imagen = None
                    self.enviar_mensaje(noticia)
                    
        except Exception as e:
            logger.error(f"💥 Error de conexión con Telegram: {e}")

# ==============================================================================
# 💾 GESTOR DE MEMORIA: EL ARCHIVISTA
# ==============================================================================
class MemoryManager:
    """Evita que el bot repita noticias usando un archivo de persistencia."""
    FILE_NAME = "last_news_id.txt"

    @classmethod
    def leer_ultimo_id(cls):
        if os.path.exists(cls.FILE_NAME):
            with open(cls.FILE_NAME, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    @classmethod
    def guardar_nuevo_id(cls, guid):
        try:
            with open(cls.FILE_NAME, "w", encoding="utf-8") as f:
                f.write(str(guid))
            logger.info(f"💾 Memoria actualizada con ID: {guid}")
        except Exception as e:
            logger.error(f"❌ Error al escribir en memoria: {e}")

# ==============================================================================
# 🚀 NÚCLEO PRINCIPAL (MAIN ORCHESTRATOR)
# ==============================================================================
def ejecutar_titan_noticias():
    """Función maestra que orquesta todo el flujo del bot."""
    logger.info("==== 🟢 INICIANDO TITÁN NEWS MEGALODÓN v20.0 ====")
    
    # 1. Instanciar motores
    scraper = ScraperEngine()
    dispatcher = TelegramDispatcher()
    
    # 2. Obtener noticia candidata
    noticia_candidata = scraper.obtener_rss_data()
    
    if not noticia_candidata:
        logger.warning("📭 No se ha podido obtener ninguna noticia válida en esta ronda.")
        return

    # 3. Comprobar si es repetida
    last_id = MemoryManager.leer_ultimo_id()
    if noticia_candidata.guid == last_id:
        logger.info(f"😴 Noticia repetida detectada ({noticia_candidata.guid}). Abortando misión.")
        return

    # 4. Enriquecer noticia con imagen
    noticia_enriquecida = scraper.capturar_imagen_principal(noticia_candidata)
    
    # 5. Despachar a Telegram
    dispatcher.enviar_mensaje(noticia_enriquecida)
    
    # 6. Si se envió con éxito, guardar en memoria
    if dispatcher.diagnostico_exitoso:
        MemoryManager.guardar_nuevo_id(noticia_enriquecida.guid)
        logger.info(f"🏁 CICLO COMPLETADO: {noticia_enriquecida.titulo[:40]}...")
    else:
        logger.error("🏁 CICLO FALLIDO: No se pudo confirmar el envío.")

if __name__ == "__main__":
    # Iniciar cronómetro de ejecución
    start_time = time.time()
    
    try:
        ejecutar_titan_noticias()
    except Exception:
        logger.critical(f"💀 FALLO CATASTRÓFICO DEL SISTEMA:\n{traceback.format_exc()}")
    
    end_time = time.time()
    logger.info(f"⏱️ Tiempo total de ejecución: {round(end_time - start_time, 2)} segundos.")
    logger.info("==== 🔴 APAGANDO SISTEMA TITÁN ====")
