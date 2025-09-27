"""
@author João Gabriel de Almeida
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente e configurar logging
load_dotenv()
from config import setup_logging, Config
setup_logging()

# Configurar logger
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="VerifficAI - API de Detecção de Fraudes em Vídeos",
    description="API para análise de conteúdo de vídeos do Instagram e detecção de fraudes",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models Pydantic
class VideoAnalysisRequest(BaseModel):
    url: str

class VideoAnalysisResponse(BaseModel):
    is_fraudulent: bool
    confidence: float
    analysis: str
    video_path: Optional[str] = None

# Importar serviços
from services.instagram_downloader import InstagramDownloader
from services.gemini_analyzer import GeminiAnalyzer

# Inicializar serviços
try:
    instagram_downloader = InstagramDownloader()
    gemini_analyzer = GeminiAnalyzer()
    logger.info("Serviços inicializados com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar serviços: {str(e)}")
    raise

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {"message": "VerifficAI API - Detecção de Fraudes em Vídeos do Instagram"}

@app.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalysisRequest):
    """
    Analisa um vídeo do Instagram para detectar fraudes

    - **url**: URL do post, story ou reel do Instagram
    """
    logger.info(f"Iniciando análise para URL: {request.url}")

    try:
        # Validar URL
        if not request.url or not self._is_instagram_url(request.url):
            raise HTTPException(status_code=400, detail="URL do Instagram inválida")

        # Baixar vídeo do Instagram
        logger.info("Baixando vídeo do Instagram...")
        video_path = await instagram_downloader.download_video(request.url)

        # Verificar tamanho do arquivo
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > Config.MAX_VIDEO_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"Vídeo muito grande: {file_size_mb".1f"}MB. Máximo permitido: {Config.MAX_VIDEO_SIZE_MB}MB"
            )

        # Analisar com Gemini
        logger.info("Analisando vídeo com Gemini...")
        analysis_result = await gemini_analyzer.analyze_video(video_path)

        logger.info(f"Análise concluída. Fraudulento: {analysis_result['is_fraudulent']}, Confiança: {analysis_result['confidence']".2f"}")

        return VideoAnalysisResponse(
            is_fraudulent=analysis_result["is_fraudulent"],
            confidence=analysis_result["confidence"],
            analysis=analysis_result["analysis"],
            video_path=video_path
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro durante análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

    def _is_instagram_url(self, url: str) -> bool:
        """Verifica se a URL é do Instagram"""
        import re
        instagram_pattern = r'https?://(www\.)?instagram\.com/(p|reel|tv)/[a-zA-Z0-9_-]+/?'
        return bool(re.match(instagram_pattern, url))

@app.get("/health")
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "gemini_configured": bool(Config.GEMINI_API_KEY),
        "debug_mode": Config.DEBUG,
        "max_video_size_mb": Config.MAX_VIDEO_SIZE_MB,
        "temp_dir": Config.TEMP_DIR
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando servidor em {Config.HOST}:{Config.PORT}")
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    )
