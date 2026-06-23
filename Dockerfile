FROM mcr.microsoft.com/playwright/python:v1.41.2-jammy

WORKDIR /app

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Nota: A imagem oficial do Playwright já vem com os navegadores (Chromium) 
# e todas as dependências do sistema operacional instaladas de fábrica, 
# então não precisamos mais rodar o "playwright install-deps"!

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020", "--forwarded-allow-ips", "*"]
