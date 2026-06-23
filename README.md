# Microsserviço de Comissões e Colegiados USP

Este é um microsserviço desenvolvido em Python (FastAPI) para extrair, armazenar e disponibilizar os dados de comissões e colegiados da USP para um site WordPress.

## Tecnologias Utilizadas

- **FastAPI**: Framework web principal.
- **Jinja2**: Motor de templates para a área administrativa e renderização do HTML exportado.
- **Playwright**: Utilizado para o Web Scraping nas páginas (Vue.js/SPAs) da USP.
- **SQLite + SQLAlchemy**: Banco de dados e ORM.
- **APScheduler**: Agendamento de tarefas (scraping na madrugada).
- **Docker**: Containerização.

## Como Executar

1. Copie o arquivo de configuração e edite se necessário:
   ```bash
   cp .env.example .env
   ```

2. Suba a aplicação via Docker:
   ```bash
   docker-compose up -d --build
   ```

3. Acesse a Área Administrativa:
   - **URL:** `http://localhost:8020/admin/login`
   - **Credenciais padrão:** `admin` / `adminusp` (ou o que você configurou no `.env`).

## Integração com WordPress

A integração é feita utilizando o arquivo `wordpress-shortcode.php` que contém o shortcode `[ime_comissoes]`. Este shortcode consome a API que roda em `http://localhost:8020/api/comissoes/html` e injeta a visualização em formato accordion na sua página.

## Personalizando o Web Scraping

Você deverá acessar o arquivo `app/scraper.py` e ajustar os seletores (`query_selector_all` etc.) de acordo com a estrutura e as classes CSS exatas das páginas Vue.js que hospedam os dados reais das comissões na USP.
