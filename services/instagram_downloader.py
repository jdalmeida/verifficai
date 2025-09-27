"""
@author João Gabriel de Almeida
"""

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
            # Verificar se é uma URL de story (que pode não ser suportada)
            if '/stories/' in url:
                raise ValueError("URLs de stories do Instagram não são suportadas. Use apenas posts ou reels.")

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
            from config import Config
            temp_dir = Config.TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            # Configurar diretório de download
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Baixar o vídeo
                self.loader.download_post(post, target="temp")

                # Procurar arquivo de vídeo (incluindo subdiretórios)
                video_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.mp4'):
                            video_files.append(os.path.join(root, file))

                if not video_files:
                    raise ValueError("Vídeo não encontrado no post")

                # Pegar o primeiro arquivo de vídeo (geralmente o principal)
                temp_video_path = video_files[0]

                logger.info(f"Vídeo encontrado em: {temp_video_path}")
                logger.info(f"Arquivo existe: {os.path.exists(temp_video_path)}")

                # Copiar para um arquivo temporário mais persistente
                import shutil
                import uuid
                final_video_path = os.path.join(temp_dir, f"video_{shortcode}_{uuid.uuid4().hex[:8]}.mp4")

                try:
                    shutil.copy2(temp_video_path, final_video_path)
                    logger.info(f"Vídeo copiado para: {final_video_path}")
                    logger.info(f"Arquivo copiado existe: {os.path.exists(final_video_path)}")
                except Exception as copy_error:
                    logger.error(f"Erro ao copiar arquivo: {copy_error}")
                    raise ValueError(f"Erro ao processar vídeo: {copy_error}")

                # Retornar caminho do arquivo copiado
                return final_video_path

            finally:
                os.chdir(original_dir)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao baixar vídeo: {error_msg}")

            # Melhorar mensagens de erro comuns
            if "403" in error_msg or "Forbidden" in error_msg:
                error_msg = "Acesso bloqueado pelo Instagram. Tente novamente mais tarde ou use uma VPN."
            elif "Post metadata failed" in error_msg:
                error_msg = "Não foi possível acessar os metadados do post. O post pode ser privado ou não existir."
            elif "not found" in error_msg.lower():
                error_msg = "Post não encontrado. Verifique se a URL está correta e o post é público."

            raise ValueError(f"Não foi possível baixar o vídeo: {error_msg}")

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
            r'instagram\.com/tv/([a-zA-Z0-9_-]+)',
            r'instagram\.com/stories/[^/]+/([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None
