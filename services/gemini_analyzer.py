"""
@author João Gabriel de Almeida
"""

import google.generativeai as genai
import os
import logging
from typing import Dict, Any
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Serviço para análise de vídeos usando o Google Gemini"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        genai.configure(api_key=api_key)
        from config import Config
        # Usar modelo configurado (padrão: gemini-1.5-flash para análise de imagens)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    async def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Analisa um vídeo para detectar fraudes e conteúdo gerado por IA

        Args:
            video_path: Caminho local do arquivo de vídeo

        Returns:
            Dicionário com resultado da análise
        """
        try:
            # Para análise de vídeo, precisamos extrair frames
            # O Gemini Vision funciona melhor com imagens
            frames = await self._extract_video_frames(video_path)

            # Analisar frames para detectar características de IA e fraudes
            analysis_results = []

            for i, frame_path in enumerate(frames[:5]):  # Limitar a 5 frames para performance
                try:
                    frame_analysis = await self._analyze_frame(frame_path, i + 1, len(frames))
                    analysis_results.append(frame_analysis)
                except Exception as e:
                    logger.warning(f"Erro ao analisar frame {i+1}: {str(e)}")
                    continue

            if not analysis_results:
                raise ValueError("Não foi possível analisar nenhum frame do vídeo")

            # Consolidar resultados
            final_result = self._consolidate_analysis(analysis_results)

            return final_result

        except Exception as e:
            logger.error(f"Erro na análise do vídeo: {str(e)}")
            raise ValueError(f"Erro na análise: {str(e)}")

    async def _extract_video_frames(self, video_path: str) -> list:
        """
        Extrai frames de um vídeo para análise

        Args:
            video_path: Caminho do arquivo de vídeo

        Returns:
            Lista de caminhos dos frames extraídos
        """
        import cv2
        import tempfile
        import os

        frames = []
        temp_dir = tempfile.mkdtemp()

        try:
            # Abrir vídeo
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                raise ValueError("Não foi possível abrir o arquivo de vídeo")

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Extrair frames em intervalos regulares (máximo 10 frames)
            frame_interval = max(1, total_frames // 10)

            frame_count = 0
            extracted_count = 0

            while cap.isOpened() and extracted_count < 10:
                ret, frame = cap.read()

                if not ret:
                    break

                # Salvar frame se estiver no intervalo correto
                if frame_count % frame_interval == 0:
                    frame_filename = f"frame_{extracted_count:03d}.jpg"
                    frame_path = os.path.join(temp_dir, frame_filename)

                    # Redimensionar frame para análise (otimização)
                    height, width = frame.shape[:2]
                    if width > 1024:
                        new_width = 1024
                        new_height = int(height * new_width / width)
                        frame = cv2.resize(frame, (new_width, new_height))

                    cv2.imwrite(frame_path, frame)
                    frames.append(frame_path)
                    extracted_count += 1

                frame_count += 1

            cap.release()

        except Exception as e:
            logger.error(f"Erro ao extrair frames: {str(e)}")
            raise

        return frames

    async def _analyze_frame(self, frame_path: str, frame_number: int, total_frames: int) -> Dict[str, Any]:
        """
        Analisa um frame individual

        Args:
            frame_path: Caminho do frame
            frame_number: Número do frame
            total_frames: Total de frames do vídeo

        Returns:
            Resultado da análise do frame
        """
        try:
            # Carregar imagem
            from PIL import Image
            image = Image.open(frame_path)

            # Prompt específico para detecção de fraudes em anúncios
            prompt = """
            Analise esta imagem de um anúncio de venda e determine se há indícios de fraude ou se foi gerada por IA.

            Foque nestes aspectos:
            1. Qualidade visual inconsistente ou artificial
            2. Elementos que parecem gerados por computador
            3. Inconsistências na iluminação, sombras ou reflexos
            4. Textos ou preços que parecem suspeitos
            5. Produtos que parecem não existir ou ter características impossíveis
            6. Cenários ou fundos que parecem falsos

            Esta é uma análise de frame {frame_number} de {total_frames} de um vídeo.

            Responda apenas com:
            - FRAUDULENTO: sim/não
            - CONFIANCA: valor entre 0.0 e 1.0
            - MOTIVOS: lista de motivos encontrados
            """

            # Fazer análise com Gemini
            response = self.model.generate_content([prompt, image])

            if not response or not response.text:
                raise ValueError("Resposta vazia do Gemini")

            # Processar resposta
            result = self._parse_gemini_response(response.text)

            return {
                "frame_number": frame_number,
                "is_fraudulent": result["is_fraudulent"],
                "confidence": result["confidence"],
                "reasons": result["reasons"]
            }

        except Exception as e:
            logger.error(f"Erro ao analisar frame {frame_number}: {str(e)}")
            raise

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Processa a resposta do Gemini

        Args:
            response_text: Texto de resposta do Gemini

        Returns:
            Dicionário com dados extraídos
        """
        lines = response_text.strip().split('\n')

        is_fraudulent = False
        confidence = 0.5
        reasons = []

        for line in lines:
            line = line.strip().upper()

            if 'FRAUDULENTO: SIM' in line:
                is_fraudulent = True
            elif 'FRAUDULENTO: NÃO' in line or 'FRAUDULENTO: NAO' in line:
                is_fraudulent = False
            elif 'CONFIANCA:' in line or 'CONFIANÇA:' in line:
                try:
                    conf_value = line.split(':')[1].strip()
                    confidence = float(conf_value)
                except:
                    pass
            elif 'MOTIVOS:' in line:
                # Capturar motivos da próxima linha ou restantes
                reason_text = line.split(':', 1)[1].strip() if ':' in line else ""
                if reason_text:
                    reasons = [r.strip() for r in reason_text.split(',') if r.strip()]
                # Se não encontrou motivos na linha, tenta a próxima
                elif len(lines) > len([l for l in lines if 'MOTIVOS:' in l.upper()]):
                    next_lines = [l for l in lines if 'MOTIVOS:' in l.upper()]
                    if next_lines:
                        idx = lines.index(next_lines[0])
                        if idx + 1 < len(lines):
                            reasons = [lines[idx + 1].strip()]

        return {
            "is_fraudulent": is_fraudulent,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasons": reasons
        }

    def _consolidate_analysis(self, analysis_results: list) -> Dict[str, Any]:
        """
        Consolida os resultados de análise de múltiplos frames

        Args:
            analysis_results: Lista de resultados de análise de frames

        Returns:
            Resultado consolidado
        """
        if not analysis_results:
            return {
                "is_fraudulent": False,
                "confidence": 0.0,
                "analysis": "Não foi possível realizar análise suficiente"
            }

        # Calcular médias e consolidar
        fraudulent_count = sum(1 for r in analysis_results if r["is_fraudulent"])
        total_frames = len(analysis_results)

        fraudulent_ratio = fraudulent_count / total_frames
        avg_confidence = sum(r["confidence"] for r in analysis_results) / total_frames

        # Consolidar motivos
        all_reasons = []
        for result in analysis_results:
            all_reasons.extend(result.get("reasons", []))

        # Determinar se é fraudulento baseado na maioria dos frames
        is_fraudulent = fraudulent_ratio >= 0.6  # Pelo menos 60% dos frames indicam fraude

        # Ajustar confiança baseado na consistência
        confidence_consistency = 1.0 - (sum(abs(r["confidence"] - avg_confidence) for r in analysis_results) / total_frames)
        final_confidence = (avg_confidence + confidence_consistency) / 2

        # Gerar análise textual
        if is_fraudulent:
            analysis = f"Detectada possível fraude em {fraudulent_count}/{total_frames} frames analisados. "
            if all_reasons:
                analysis += f"Motivos identificados: {', '.join(set(all_reasons))}"
            else:
                analysis += "Análise indica características suspeitas consistentes com conteúdo fraudulento."
        else:
            analysis = f"Análise de {total_frames} frames não detectou indícios significativos de fraude. "
            analysis += f"Confiança na análise: {final_confidence:.2f}"

        return {
            "is_fraudulent": is_fraudulent,
            "confidence": final_confidence,
            "analysis": analysis,
            "frames_analyzed": total_frames,
            "fraudulent_frames": fraudulent_count,
            "reasons": list(set(all_reasons))
        }
