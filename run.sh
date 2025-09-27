#!/bin/bash


# Script de inicialização da API VerifficAI

echo "🚀 Iniciando VerifficAI API..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3 e tente novamente."
    exit 1
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando .env.example..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Configure sua GEMINI_API_KEY antes de continuar."
    echo "   Edite o arquivo .env e adicione sua chave da API do Gemini."
    exit 1
fi

# Verificar se GEMINI_API_KEY está configurada
if ! grep -q "GEMINI_API_KEY=.*[^[:space:]]" .env; then
    echo "⚠️  GEMINI_API_KEY não configurada no arquivo .env"
    echo "   Configure sua chave da API do Gemini antes de continuar."
    exit 1
fi

# Instalar dependências se necessário
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "📦 Instalando dependências..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Verificar se as dependências estão instaladas
if ! python3 -c "import fastapi, uvicorn, google.generativeai" &> /dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Iniciar a API
echo "🔄 Iniciando servidor..."
python3 main.py

echo "✅ API iniciada com sucesso!"
