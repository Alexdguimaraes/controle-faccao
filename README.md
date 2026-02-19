# G.A. Facção - Versão Mobile para Android

Este é o projeto mobile do Sistema de Controle de Facção, desenvolvido com **Kivy** e **KivyMD** para Android.

## 📱 Requisitos

### Para Desenvolvimento:
- Python 3.8+
- Kivy 2.2+
- KivyMD 1.1+

### Para Build Android:
- Ubuntu 20.04+ (recomendado) ou WSL2
- Buildozer
- Cython
- Android SDK/NDK (instalados automaticamente)

---

## 🚀 Instalação para Desenvolvimento

### 1. Criar ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências:
```bash
pip install kivy==2.2.1 kivymd==1.1.1 pillow
```

### 3. Testar no desktop:
```bash
python main.py
```

---

## 📦 Build para Android

### Opção 1: Usando Buildozer (Recomendado)

#### 1. Instalar Buildozer no Ubuntu/WSL2:
```bash
# Instalar dependências
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Instalar buildozer
pip3 install buildozer cython
```

#### 2. Configurar o projeto:
```bash
cd faccao_mobile
```

#### 3. Fazer o build (primeira vez demora ~30-60 min):
```bash
# Build de debug
buildozer android debug

# Build de release
buildozer android release
```

#### 4. O APK será gerado em:
```
bin/faccao_controle-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

#### 5. Instalar no celular:
```bash
# Conectar celular via USB com debug ativado
buildozer android deploy run

# Ou copiar APK manualmente para o celular
```

---

### Opção 2: Usando Docker (Mais fácil)

```bash
# Baixar imagem do buildozer
docker pull kivy/buildozer

# Rodar build
docker run --rm -v "$(pwd)":/home/user/hostcwd kivy/buildozer android debug
```

---

### Opção 3: Usando Google Colab (Sem instalar nada)

1. Acesse: https://colab.research.google.com/
2. Crie um novo notebook
3. Execute os comandos:

```python
# Upload do projeto
from google.colab import files
import zipfile
import os

# Fazer upload do zip do projeto
uploaded = files.upload()

# Extrair
for filename in uploaded.keys():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('/content/')

# Instalar buildozer
!pip install buildozer cython

# Instalar dependências Android
!apt update
!apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev

# Build
%cd /content/faccao_mobile
!buildozer android debug

# Download do APK
from google.colab import files
files.download('bin/faccao_controle-2.0.0-arm64-v8a_armeabi-v7a-debug.apk')
```

---

## 🔧 Comandos Úteis do Buildozer

```bash
# Limpar build anterior
buildozer android clean

# Build debug
buildozer android debug

# Build release (assinado)
buildozer android release

# Deploy e run no dispositivo
buildozer android deploy run

# Ver logs do app
buildozer android logcat

# Ver especificações do dispositivo
buildozer android adb -- devices
```

---

## 📋 Solução de Problemas

### Erro: "No module named 'android'"
```bash
# Adicionar ao buildozer.spec:
requirements = python3,kivy==2.2.1,kivymd==1.1.1,android
```

### Erro: "SDK not found"
```bash
# Instalar SDK manualmente
buildozer android sdk
```

### Erro de memória:
```bash
# Aumentar memória do Java
export JAVA_OPTS="-Xmx4g"
```

### App fecha ao abrir:
```bash
# Ver logs
buildozer android logcat | grep python
```

---

## 🎨 Personalização

### Ícone do App:
1. Crie um ícone PNG 512x512
2. Salve em `assets/icon.png`
3. Descomente no buildozer.spec:
```ini
icon.filename = %(source.dir)s/assets/icon.png
```

### Splash Screen:
1. Crie uma imagem PNG
2. Salve em `assets/presplash.png`
3. Descomente no buildozer.spec:
```ini
presplash.filename = %(source.dir)s/assets/presplash.png
```

### Cores do Tema:
Edite `main.py` e altere:
```python
self.theme_cls.primary_palette = 'Blue'  # Cor primária
self.theme_cls.accent_palette = 'Green'  # Cor de destaque
self.theme_cls.theme_style = 'Light'     # 'Light' ou 'Dark'
```

---

## 📱 Funcionalidades Mobile

### ✅ Implementadas:
- [x] Login seguro
- [x] Dashboard com KPIs
- [x] Lista de clientes
- [x] Controle de produção (OPs)
- [x] Registro de entregas
- [x] Financeiro (contas a receber)
- [x] Liquidação de títulos
- [x] Interface responsiva
- [x] Navegação por abas

### 🚧 Em Desenvolvimento:
- [ ] Estoque
- [ ] Despesas
- [ ] Relatórios
- [ ] Backup na nuvem
- [ ] Sincronização
- [ ] Notificações push

---

## 🌐 Publicação na Play Store

### 1. Gerar keystore (apenas uma vez):
```bash
keytool -genkey -v -keystore faccao.keystore -alias faccao -keyalg RSA -keysize 2048 -validity 10000
```

### 2. Configurar no buildozer.spec:
```ini
android.release_artifact = aab
```

### 3. Build de release:
```bash
buildozer android release
```

### 4. Upload na Play Store Console:
- Acesse: https://play.google.com/console
- Crie nova app
- Faça upload do AAB

---

## 📞 Suporte

Em caso de dúvidas ou problemas:
- Documentação Kivy: https://kivy.org/doc/stable/
- Documentação KivyMD: https://kivymd.readthedocs.io/
- Documentação Buildozer: https://buildozer.readthedocs.io/

---

**Versão**: 2.0.0 Mobile  
**Desenvolvido com**: Python + Kivy + KivyMD
