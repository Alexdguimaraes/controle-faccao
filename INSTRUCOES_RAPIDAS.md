# 🚀 Instruções Rápidas - Build Android

## Opção 1: Google Colab (Mais Fácil - Sem Instalar Nada)

1. Acesse: https://colab.research.google.com/
2. Crie novo notebook
3. Cole e execute:

```python
# 1. Fazer upload do projeto
from google.colab import files
uploaded = files.upload()  # Selecione o faccao_mobile.zip

# 2. Extrair
import zipfile
for f in uploaded.keys():
    zipfile.ZipFile(f).extractall('/content/')

# 3. Instalar dependências
!apt update -qq
!apt install -y -qq git zip unzip openjdk-17-jdk
!pip install -q buildozer cython

# 4. Build
%cd /content/faccao_mobile
!buildozer android debug 2>&1 | tail -100

# 5. Download do APK
files.download('bin/faccao_controle-2.0.0-arm64-v8a_armeabi-v7a-debug.apk')
```

---

## Opção 2: Ubuntu/WSL2 (Local)

### 1. Instalar dependências:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
pip3 install buildozer cython
```

### 2. Build:
```bash
cd faccao_mobile
chmod +x build.sh
./build.sh
# Escolha opção 1 (Debug)
```

### 3. APK gerado em:
```
bin/faccao_controle-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

## 📱 Instalar no Celular

### Opção A - USB:
```bash
buildozer android deploy run
```

### Opção B - Manual:
1. Copie o APK para o celular
2. No celular, ative: **Configurações > Segurança > Fontes desconhecidas**
3. Instale o APK

---

## ⚠️ Primeiro Build

⏱️ **Demora 30-60 minutos** (baixa Android SDK/NDK)

Builds seguintes são mais rápidos (~5 min)

---

## 🐛 Problemas Comuns

| Problema | Solução |
|----------|---------|
| "SDK not found" | `buildozer android sdk` |
| Falta de memória | `export JAVA_OPTS="-Xmx4g"` |
| App fecha | `buildozer android logcat` |
| Build falha | `buildozer android clean` e tente novamente |

---

**Dúvidas?** Veja README.md completo
