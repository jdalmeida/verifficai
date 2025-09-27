# VerifficAI - API de Detecção de Fraudes em Vídeos do Instagram

API em Python para análise de conteúdo de vídeos do Instagram e detecção de fraudes, com foco especial em anúncios de venda.

## Funcionalidades

- ✅ Download automático de vídeos do Instagram (posts, reels)
- ✅ Análise avançada com Google Gemini Vision
- ✅ Detecção de conteúdo gerado por IA
- ✅ Identificação de fraudes em anúncios de venda
- ✅ Análise de múltiplos frames do vídeo
- ✅ API RESTful com FastAPI

## Instalação

### 1. Clonagem e dependências

```bash
cd /home/jalmeida/desenv/verifficai/api-python
pip install -r requirements.txt
# ou
pnpm install  # se usar pnpm
```

### 2. Configuração da API do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Crie uma chave de API
3. Configure a variável de ambiente:

```bash
# Edite o arquivo .env
GEMINI_API_KEY=sua-chave-aqui
```

### 3. Executar a API

```bash
python main.py
# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`

## Uso da API

### Endpoint de análise

**POST** `/analyze`

Análise um vídeo do Instagram para detectar fraudes.

**Request:**
```json
{
  "url": "https://www.instagram.com/p/CODE_EXAMPLE/"
}
```

**Response:**
```json
{
  "is_fraudulent": true,
  "confidence": 0.85,
  "analysis": "Detectada possível fraude... Motivos: iluminação inconsistente, sombras artificiais",
  "video_path": "/tmp/temp_video.mp4",
  "frames_analyzed": 8,
  "fraudulent_frames": 6,
  "reasons": ["iluminação inconsistente", "sombras artificiais"]
}
```

### Endpoint de saúde

**GET** `/health`

Verifica se a API está funcionando corretamente.

## Como funciona

1. **Download**: A API extrai o shortcode da URL do Instagram e baixa o vídeo
2. **Extração de frames**: O vídeo é processado e frames são extraídos em intervalos regulares
3. **Análise IA**: Cada frame é enviado para o Google Gemini Vision com prompts específicos para detecção de fraudes
4. **Consolidação**: Os resultados são consolidados para dar uma resposta final
5. **Resposta**: A API retorna se o conteúdo é fraudulento, com nível de confiança e motivos

## Tipos de fraude detectados

- ✅ Vídeos gerados por inteligência artificial
- ✅ Anúncios falsos de produtos
- ✅ Manipulação digital de imagens
- ✅ Inconsistências visuais suspeitas
- ✅ Textos e preços fraudulentos

## Tecnologias utilizadas

- **FastAPI**: Framework web moderno e rápido
- **Google Gemini Vision**: IA para análise de imagens/vídeos
- **Instaloader**: Download de conteúdo do Instagram
- **OpenCV**: Processamento de vídeo e extração de frames
- **PIL**: Manipulação de imagens

## Configuração avançada

### Variáveis de ambiente

```env
GEMINI_API_KEY=sua-chave-aqui          # Obrigatório
PORT=8000                             # Porta do servidor
HOST=0.0.0.0                         # Host do servidor
DEBUG=true                           # Modo debug
LOG_LEVEL=INFO                       # Nível de logging
TEMP_DIR=/tmp/verifficai             # Diretório temporário
MAX_VIDEO_SIZE_MB=100               # Tamanho máximo do vídeo (MB)
```

### Logging

A aplicação gera logs em:
- Console (stdout)
- Arquivo `verifficai.log`

## Limitações

- ⚠️ **Stories não suportadas**: URLs de stories do Instagram não podem ser processadas
- 🔒 **Apenas posts públicos**: Posts privados não podem ser acessados
- 🚦 **Rate limiting**: O Instagram pode bloquear acessos frequentes
- ⏱️ **Processamento lento**: Vídeos longos podem demorar para analisar
- 🔑 **Requer API key**: Necessária chave válida do Google Gemini
- 🌐 **Dependência externa**: Funciona apenas quando APIs externas estão disponíveis

## Desenvolvimento

### Estrutura do projeto

```
api-python/
├── main.py                    # Arquivo principal da API
├── config.py                  # Configurações da aplicação
├── requirements.txt           # Dependências Python
├── .env                      # Variáveis de ambiente
├── README.md                 # Esta documentação
└── services/
    ├── instagram_downloader.py    # Download de vídeos IG
    └── gemini_analyzer.py         # Análise com Gemini
```

### Adicionar novos tipos de análise

Para adicionar novos tipos de detecção de fraude:

1. Edite `gemini_analyzer.py`
2. Modifique o prompt de análise
3. Adicione novos campos na resposta
4. Atualize os modelos Pydantic

## Suporte

Para suporte e dúvidas, entre em contato com o desenvolvedor.

---

**Desenvolvido por João Gabriel de Almeida**
