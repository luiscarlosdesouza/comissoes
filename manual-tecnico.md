# Manual Técnico — Sistema de Comissões IME/USP

## 1. Objetivo

Este documento descreve a instalação, configuração e uso do sistema de comissões do IME/USP, que:

- coleta dados das páginas externas da USP;
- armazena cache local;
- expõe uma API em Python;
- integra com o WordPress por meio de shortcode;
- permite exibição em blocos separados, por comissão, categoria ou lista personalizada.

---

## 2. Visão geral da arquitetura

### Componentes

- **Backend Python**
  - FastAPI
  - Playwright
  - SQLite
  - APScheduler
  - Jinja2

- **Frontend WordPress**
  - Gutenberg
  - shortcode PHP
  - plugin de snippets ou plugin customizado

- **Deploy**
  - Docker
  - docker-compose
  - porta **8020**

---

## 3. Pré-requisitos

Antes de instalar, confirme que você tem:

- **Git**
- **Docker**
- **Docker Compose**
- Acesso ao **GitHub**
- Acesso ao **WordPress**
- Permissão de administrador no servidor de homologação ou produção

---

## 4. Estrutura esperada do projeto

O projeto está organizado no diretório:

```text
/sistemas/comissoes/
```

Estrutura principal:

```text
/sistemas/comissoes/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── scraper.py
│   ├── scheduler.py
│   ├── seed.py
│   ├── routes/
│   │   ├── api.py
│   │   └── admin.py
│   └── templates/
│       ├── admin/
│       └── public/
├── wordpress/
│   └── shortcode.php
└── data/
    ├── db.sqlite3
    └── cache/
```

---

## 5. Instalação local para testes

### 5.1 Clonar o repositório

```bash
cd /sistemas
git clone https://github.com/luiscarlosdesouza/comissoes.git comissoes
cd /sistemas/comissoes
```

### 5.2 Criar o arquivo `.env`

Crie o arquivo `.env` com os valores reais do ambiente:

```env
ADMIN_USER=admin
ADMIN_PASSWORD=senha_forte_aqui
SECRET_KEY=uma_chave_longa_e_aleatoria
TZ=America/Sao_Paulo
AMBIENTE=homologacao
```

### 5.3 Criar as pastas necessárias

```bash
mkdir -p data/cache
```

### 5.4 Build dos containers

```bash
docker compose build
```

### 5.5 Criar banco e popular com as comissões

```bash
docker compose run --rm app python app/database.py
docker compose run --rm app python app/seed.py
```

### 5.6 Subir a aplicação

```bash
docker compose up -d
```

### 5.7 Testar a API

```bash
curl http://localhost:8020/api/comissoes
```

---

## 6. Instalação no servidor de homologação

### 6.1 Acessar o servidor

```bash
ssh usuario@ip-do-servidor
```

### 6.2 Criar a pasta do projeto

```bash
mkdir -p /sistemas/comissoes
cd /sistemas/comissoes
```

### 6.3 Clonar o repositório

```bash
git clone https://github.com/luiscarlosdesouza/comissoes.git .
```

### 6.4 Criar o `.env`

```bash
cat > .env << 'EOF'
ADMIN_USER=admin
ADMIN_PASSWORD=senha_forte_aqui
SECRET_KEY=uma_chave_longa_e_aleatoria
TZ=America/Sao_Paulo
AMBIENTE=homologacao
EOF
```

### 6.5 Criar diretórios

```bash
mkdir -p data/cache
```

### 6.6 Build e inicialização

```bash
docker compose build
docker compose run --rm app python app/database.py
docker compose run --rm app python app/seed.py
docker compose up -d
```

---

## 7. Variáveis de ambiente

### 7.1 Variáveis obrigatórias

| Variável | Finalidade |
|---|---|
| `ADMIN_USER` | Usuário do painel administrativo |
| `ADMIN_PASSWORD` | Senha do painel administrativo |
| `SECRET_KEY` | Chave para sessões e autenticação |
| `TZ` | Fuso horário do servidor |
| `AMBIENTE` | Identifica homologação ou produção |

### 7.2 Observação sobre a URL da API

Se o WordPress estiver em outro servidor, a URL da API usada pelo shortcode pode precisar ser ajustada no código PHP.

Exemplo:

```text
http://www2.ime.usp.br:8020/api
```

---

## 8. Instalação do shortcode no WordPress

O WordPress usará o shortcode para mostrar as comissões na página.

### 8.1 Opção recomendada: plugin de snippets

Uma forma prática é usar um plugin de snippets, como o **Code Snippets**.

#### Passos:

1. Entre no painel WordPress
2. Vá em **Plugins → Adicionar novo**
3. Pesquise por **Code Snippets**
4. Instale e ative
5. Crie um novo snippet
6. Cole o código do arquivo `wordpress/shortcode.php`
7. Salve e ative o snippet

### 8.2 Opção alternativa: plugin customizado

Se preferir, você pode criar um plugin próprio com o código do shortcode.

Estrutura exemplo:

```text
wp-content/plugins/ime-usp-comissoes/
└── ime-usp-comissoes.php
```

---

## 9. Nome do shortcode

O shortcode principal deve ser:

```text
[ime_comissoes]
```

Outras variações possíveis:

```text
[ime_comissoes id="14"]
[ime_comissoes ids="13,14,15"]
[ime_comissoes tipo="conselhos-departamento"]
```

---

## 10. Como inserir o shortcode no Gutenberg

### 10.1 Abrir a página

1. Vá em **Páginas → Todas as páginas**
2. Clique em **Editar**

### 10.2 Adicionar bloco de shortcode

1. Clique no botão **+**
2. Procure por **Shortcode**
3. Adicione o bloco
4. Cole o shortcode desejado

### 10.3 Exemplo

```text
[ime_comissoes tipo="conselhos-departamento"]
```

### 10.4 Salvar

- Clique em **Atualizar**
- Depois clique em **Visualizar**

---

## 11. Exemplos de uso

### 11.1 Todas as comissões

```text
[ime_comissoes]
```

### 11.2 Uma comissão específica

```text
[ime_comissoes id="14"]
```

### 11.3 Lista manual em ordem personalizada

```text
[ime_comissoes ids="14,7,22"]
```

### 11.4 Por categoria

```text
[ime_comissoes tipo="cursos-graduacao"]
```

---

## 12. Organização em páginas do WordPress

Você pode montar a página por blocos, por exemplo:

### Órgãos colegiados

```text
[ime_comissoes tipo="orgaos-colegiados"]
```

### Conselhos de departamento

```text
[ime_comissoes tipo="conselhos-departamento"]
```

### Graduação

```text
[ime_comissoes tipo="cursos-graduacao"]
```

### Pós-graduação

```text
[ime_comissoes tipo="programas-posgraduacao"]
```

### Outras comissões

```text
[ime_comissoes tipo="mais-comissoes"]
```

---

## 13. Ordem de exibição

A ordem pode ser controlada de duas formas:

### 13.1 Reordenando os blocos no Gutenberg

- basta arrastar os blocos para cima ou para baixo

### 13.2 Usando o parâmetro `ids`

Exemplo:

```text
[ime_comissoes ids="14,7,22"]
```

A lista será exibida exatamente nessa ordem.

---

## 14. Atualização automática

O sistema pode atualizar os dados automaticamente:

- em horário agendado de madrugada
- ou por acionamento manual no painel administrativo

### Benefícios

- reduz manutenção manual;
- mantém os dados atualizados;
- evita edição repetitiva no WordPress.

---

## 15. Estrutura esperada da resposta

A API pode retornar:

- título da comissão
- seções internas
- membros
- início do mandato
- fim do mandato

### Exemplo de estrutura lógica

```json
{
  "titulo": "Conselho do Departamento de Estatística",
  "secoes": [
    {
      "nome_secao": "Titulares",
      "membros": [
        {
          "nome": "Fulano de Tal",
          "inicio_mandato": "01/03/2025",
          "fim_mandato": "28/02/2027"
        }
      ]
    }
  ]
}
```

---

## 16. Botão de PDF

O HTML público pode incluir um botão para salvar em PDF.

### Comportamento esperado

- o usuário abre a comissão
- clica em **Salvar em PDF**
- o navegador abre a impressão
- o usuário salva como PDF

### Observação

O CSS de impressão deve ocultar elementos externos do WordPress e mostrar apenas o conteúdo da comissão.

---

## 17. Problemas comuns e solução

### 17.1 O shortcode aparece como texto

Exemplo:

```text
[ime_comissoes id="14"]
```

Se aparecer como texto na página:

- verifique se o snippet está ativo;
- verifique se o nome do shortcode está correto;
- confirme que ele foi inserido no bloco **Shortcode**;
- confira se as aspas são normais, e não curvas.

### 17.2 A API não responde

Verifique:

- se o container está ativo;
- se a porta **8020** está liberada;
- se o endpoint está correto;
- se a URL externa da USP continua acessível.

### 17.3 O scraper falha

Pode acontecer se:

- a página externa mudou de estrutura;
- o seletor não apareceu;
- o site da USP demorou para carregar.

Nesse caso, revise o scraper e execute novamente o seed/cache.

---

## 18. Comandos úteis

### Ver containers

```bash
docker ps
```

### Ver logs

```bash
docker compose logs -f
```

### Entrar no container

```bash
docker exec -it usp_comissoes_web bash
```

### Testar o scraper dentro do container

```bash
python -c "import asyncio, json; from app.scraper import scrape_comissao; print(json.dumps(asyncio.run(scrape_comissao('https://portalservicos.usp.br/mandato/1665/CoDepto?embedded')), indent=2, ensure_ascii=False))"
```

---

## 19. Publicação no GitHub

Antes de subir, verifique:

```bash
git status
```

Depois:

```bash
git add .
git commit -m "docs: adiciona manual tecnico do sistema"
git push origin main
```

---

## 20. Resumo rápido

### Para o servidor

```bash
git clone https://github.com/luiscarlosdesouza/comissoes.git .
docker compose build
docker compose run --rm app python app/database.py
docker compose run --rm app python app/seed.py
docker compose up -d
```

### Para o WordPress

- instalar o shortcode;
- usar o bloco **Shortcode**;
- inserir:
  - `[ime_comissoes]`
  - `[ime_comissoes id="14"]`
  - `[ime_comissoes ids="14,7,22"]`
  - `[ime_comissoes tipo="conselhos-departamento"]`

---

## 21. Observação final

Este sistema centraliza a coleta, organização e exibição das comissões do IME/USP.

Quando houver mudança na estrutura das páginas externas, pode ser necessário revisar:

- o scraper;
- o mapeamento das seções;
- a configuração da API;
- o shortcode do WordPress.