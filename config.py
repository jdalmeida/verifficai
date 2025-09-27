/**
 * @author João Gabriel de Almeida
 */

import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações da aplicação
class Config:
    """Configurações da aplicação"""

    # Configurações da API
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Configurações do Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro-vision")

    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configurações de download
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/verifficai")
    MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))

# Configurar logging
def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("verifficai.log")
        ]
    )

    # Suprimir logs verbosos de bibliotecas externas
    logging.getLogger("instaloader").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
