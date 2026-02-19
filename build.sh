#!/bin/bash
# Script de build para Android

echo "========================================"
echo "  G.A. Facção - Build Android"
echo "========================================"
echo ""

# Verificar se buildozer está instalado
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer não encontrado!"
    echo ""
    echo "Instale com:"
    echo "  pip install buildozer cython"
    echo ""
    exit 1
fi

# Menu
echo "Escolha uma opção:"
echo ""
echo "  1) Build Debug (rápido, para testes)"
echo "  2) Build Release (para publicação)"
echo "  3) Clean (limpar build anterior)"
echo "  4) Deploy no dispositivo"
echo "  5) Ver logs"
echo ""
read -p "Opção: " opcao

case $opcao in
    1)
        echo ""
        echo "🔨 Iniciando build DEBUG..."
        echo "(Isso pode levar 30-60 min na primeira vez)"
        echo ""
        buildozer android debug
        echo ""
        echo "✅ Build concluído!"
        echo "APK em: bin/"
        ls -la bin/*.apk 2>/dev/null || echo "Nenhum APK encontrado"
        ;;
    2)
        echo ""
        echo "🔨 Iniciando build RELEASE..."
        buildozer android release
        echo ""
        echo "✅ Build concluído!"
        ls -la bin/*.apk 2>/dev/null || echo "Nenhum APK encontrado"
        ;;
    3)
        echo ""
        echo "🧹 Limpando build anterior..."
        buildozer android clean
        echo "✅ Limpo!"
        ;;
    4)
        echo ""
        echo "📱 Deploy no dispositivo..."
        buildozer android deploy run
        ;;
    5)
        echo ""
        echo "📋 Logs (Ctrl+C para sair)..."
        buildozer android logcat
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac
