#!/usr/bin/env python3

"""
@author João Gabriel de Almeida
"""

"""
Exemplo de uso da API VerifficAI

Este script demonstra como usar a API para analisar vídeos do Instagram
"""

import requests
import json
import time

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Verifica se a API está funcionando"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ API está funcionando!")
            print(f"   Status: {data['status']}")
            print(f"   Gemini configurado: {data['gemini_configured']}")
            print(f"   Versão: {data['version']}")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Não foi possível conectar à API: {e}")
        return False

def analyze_instagram_video(url):
    """Analisa um vídeo do Instagram"""
    print(f"\n🔍 Analisando vídeo: {url}")

    try:
        # Preparar dados
        payload = {
            "url": url
        }

        # Fazer requisição
        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/analyze", json=payload)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print("✅ Análise concluída!"            print(f"   Tempo de análise: {end_time - start_time:.".2f"")

            print("📊 Resultados:")
            print(f"   Fraudulento: {'Sim' if result['is_fraudulent'] else 'Não'}")
            print(f"   Confiança: {result['confidence']".2f"}")
            print(f"   Frames analisados: {result.get('frames_analyzed', 'N/A')}")
            print(f"   Frames fraudulentos: {result.get('fraudulent_frames', 'N/A')}")

            print("
💬 Análise:"            print(f"   {result['analysis']}")

            if result.get('reasons'):
                print("
🚨 Motivos identificados:"                for reason in result['reasons']:
                    print(f"   • {reason}")

            return result
        else:
            print(f"❌ Erro na análise: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao fazer requisição: {e}")
        return None

def main():
    """Função principal"""
    print("🎯 VerifficAI - Exemplo de Uso")
    print("=" * 50)

    # Verificar se a API está funcionando
    if not check_api_health():
        print("\n❌ API não está disponível. Certifique-se de que está rodando em:")
        print(f"   {API_BASE_URL}")
        return

    # Exemplos de URLs para teste
    test_urls = [
        "https://www.instagram.com/p/CODE_EXAMPLE/",  # Substitua por URLs reais
        "https://www.instagram.com/reel/REAL_REEL_CODE/",
        "https://www.instagram.com/tv/VIDEO_CODE/"
    ]

    print("\n📝 Exemplos de URLs para teste:")
    for i, url in enumerate(test_urls, 1):
        print(f"   {i}. {url}")

    print("\n💡 Para usar:")
    print("   1. Substitua as URLs acima por links reais do Instagram")
    print("   2. Execute: python3 example_usage.py")
    print("   3. Ou chame analyze_instagram_video() com sua URL")

    # Exemplo de uso direto
    print("\n" + "=" * 50)
    print("🔧 Exemplo de uso programático:")

    # Descomente a linha abaixo e substitua pela sua URL
    # result = analyze_instagram_video("https://www.instagram.com/p/SEU_CODIGO_AQUI/")

if __name__ == "__main__":
    main()
