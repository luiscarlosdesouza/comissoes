# Microsserviço de Comissões e Colegiados USP

Este é um microsserviço desenvolvido em Python (FastAPI) para automatizar o web scraping, armazenar dados e disponibilizar listas de comissões e colegiados da USP para um site WordPress (ou outras plataformas).

## Tecnologias Utilizadas

- **FastAPI**: Framework web principal da API.
- **Jinja2**: Motor de templates para a área administrativa e renderização do HTML dinâmico.
- **Playwright**: Responsável pelo Web Scraping nas páginas (Vue.js/SPAs) da USP.
- **SQLite + SQLAlchemy**: Banco de dados e ORM para persistência dos dados.
- **APScheduler**: Agendamento de tarefas (scraping diário em background).
- **Docker**: Containerização completa da solução.

## Como Realizar o Deploy

1. Clone o repositório no seu servidor (produção/homologação):
   ```bash
   git clone https://github.com/luiscarlosdesouza/comissoes.git
   cd comissoes
   ```

2. Copie o arquivo de configuração e edite as credenciais de segurança e fuso horário:
   ```bash
   cp .env.example .env
   ```

3. Suba a aplicação (API e Scraper) via Docker:
   ```bash
   docker compose up -d --build
   ```

4. Crie o Banco de Dados inicial preenchendo as 47 comissões padrão e suas categorias (leitura do CSV base):
   ```bash
   docker compose exec web python app/seed.py
   ```

## Área Administrativa

- **URL:** `http://SEU-IP:8020/admin/login`
- **Credenciais padrão:** Baseadas no seu arquivo `.env` (Padrão: `admin` / `adminusp`).
- No Dashboard Administrativo, você pode cadastrar, excluir, **editar** (nome, URL e categoria mantendo o mesmo ID) e forçar a atualização (com progresso visual em tempo real) das comissões.

## Integração e Uso no WordPress

A integração com o WordPress é feita via um shortcode altamente customizável criado no arquivo `wordpress-shortcode.php`. Após instalá-lo como plugin ou copiar seu conteúdo para o `functions.php` do seu tema, você poderá utilizar o shortcode `[ime_comissoes]` das seguintes maneiras:

### 1. Todas as Comissões (Padrão)
```text
[ime_comissoes]
```
> Retorna todas as comissões do sistema no formato **Accordion** retrátil.

### 2. Filtro por Categoria
```text
[ime_comissoes tipo="conselhos-departamento"]
```
> Exibe as comissões apenas da categoria solicitada (ex: `orgaos-colegiados`, `conselhos-departamento`, `cursos-graduacao`, `programas-posgraduacao`).

### 3. Filtro de Múltiplos IDs Específicos
```text
[ime_comissoes ids="13,14,15,16"]
```
> Exibe um bloco de accordion contendo apenas as comissões selecionadas por ID, **respeitando estritamente a ordem em que você as digitou** (ex: primeiro o ID 13, depois o 14).

### 4. Visão Expandida de Comissão Única
```text
[ime_comissoes id="14"]
```
> Exibe a comissão específica já totalmente aberta (sem o estilo accordion/sanfona). Ideal para injetar dados em páginas exclusivas (ex: a página fixa da Congregação).

### 5. Layouts e Estados Personalizados (Sanfona)
Você pode usar o atributo `layout` para forçar o comportamento visual da comissão ou lista:
* **Sanfona fechada** (padrão para listas):
  ```text
  [ime_comissoes tipo="orgaos-colegiados" layout="acordeon"]
  ```
* **Sanfona aberta por padrão** (inicia aberta, mas permite clicar para fechar):
  ```text
  [ime_comissoes tipo="orgaos-colegiados" layout="acordeon-aberto"]
  ```
* **Sem sanfona / Plano** (exibe diretamente a tabela, padrão para comissão única):
  ```text
  [ime_comissoes ids="13,14" layout="plano"]
  ```

## Endpoints da API para Desenvolvedores

Caso queira integrar em outros lugares, a API expõe os seguintes endpoints principais:
- `GET /api/comissoes`: Retorna todas as comissões (com membros e categorias) em formato estrito **JSON**. (Suporta parâmetros `?ids=` e `?tipo=`)
- `GET /api/comissoes/html`: Retorna o HTML das comissões. (Suporta parâmetros `?ids=`, `?tipo=` e `?layout=`)
- `GET /api/comissao/{id}/html`: Retorna o HTML de uma única comissão. (Suporta parâmetro `?layout=`)
