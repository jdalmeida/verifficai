/**
 * @author João Gabriel de Almeida
 */

import instaloader
import re
import os
import tempfile
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class InstagramDownloader:
    """Serviço para baixar vídeos do Instagram"""

    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )

    async def download_video(self, url: str) -> str:
        """
        Baixa um vídeo do Instagram a partir de uma URL

        Args:
            url: URL do post, story ou reel do Instagram

        Returns:
            Caminho local do arquivo de vídeo baixado
        """
        try:
            # Extrair shortcode da URL
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                raise ValueError("Não foi possível extrair o código do post da URL")

            # Fazer login anônimo (sem credenciais)
            # O instaloader pode funcionar sem login para posts públicos
            try:
                self.loader.load_session_from_file("anonymous")
            except:
                # Se não conseguir carregar sessão, continua sem login
                pass

            # Obter post
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)

            # Verificar se o post existe e tem vídeo
            if not post or not post.is_video:
                raise ValueError("Post não encontrado ou não é um vídeo")

            # Criar diretório temporário para download
            with tempfile.TemporaryDirectory() as temp_dir:
                # Configurar diretório de download
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    # Baixar o vídeo
                    self.loader.download_post(post, target="temp")

                    # Procurar arquivo de vídeo
                    video_files = []
                    for file in os.listdir(temp_dir):
                        if file.endswith('.mp4'):
                            video_files.append(file)

                    if not video_files:
                        raise ValueError("Vídeo não encontrado no post")

                    # Pegar o primeiro arquivo de vídeo (geralmente o principal)
                    video_file = video_files[0]
                    video_path = os.path.join(temp_dir, video_file)

                    # Retornar caminho do arquivo
                    return video_path

                finally:
                    os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Erro ao baixar vídeo: {str(e)}")
            raise ValueError(f"Não foi possível baixar o vídeo: {str(e)}")

    def _extract_shortcode(self, url: str) -> Optional[str]:
        """
        Extrai o shortcode de uma URL do Instagram

        Args:
            url: URL do Instagram

        Returns:
            Shortcode do post ou None se não encontrado
        """
        # Padrões de URL do Instagram
        patterns = [
            r'instagram\.com/p/([a-zA-Z0-9_-]+)',
            r'instagram\.com/reel/([a-zA-Z0-9_-]+)',
            r'instagram\.com/tv/([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None
