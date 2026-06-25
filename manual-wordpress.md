# Manual de uso — Comissões e Colegiados no WordPress

## 1. Objetivo

Este sistema exibe, dentro do WordPress, a lista de comissões, conselhos, colegiados e demais órgãos do IME/USP com dados atualizados automaticamente a partir da API Python.

A visualização pública oferece:

- **Accordion/dropdown** para abrir cada comissão
- **Nome da comissão / conselho** como título
- **Lista de membros**
- **Início e fim do mandato**
- **Separação por grupos**, quando existir, como:
  - Titulares
  - Suplentes
  - Cargo
  - Tipo de representação
- **Botão para salvar em PDF**

---

## 2. Pré-requisitos

Antes de configurar a página no WordPress, verifique se:

- O serviço Python/FastAPI está rodando na porta **8020**
- O shortcode já foi instalado no WordPress
- O plugin de snippet ou o código do shortcode já está ativo
- A URL da API está correta para o ambiente:
  - homologação
  - produção

---

## 3. Estrutura geral do sistema

O sistema foi desenhado para funcionar assim:

1. O WordPress exibe a página pública
2. O shortcode PHP chama a API Python
3. A API retorna o HTML já montado
4. O HTML é renderizado no bloco da página
5. O usuário pode abrir cada comissão em accordion
6. O usuário pode imprimir ou salvar em PDF

---

## 4. Instalação do shortcode no WordPress

### 4.1 Usando plugin de snippets

No WordPress:

1. Acesse **Plugins → Adicionar novo**
2. Instale o plugin de snippets que você estiver usando
3. Crie um novo snippet
4. Cole o código do shortcode
5. Ative o snippet

### 4.2 Nome do shortcode

O shortcode principal usado no sistema é:

```text
[ime_comissoes]
```

> Importante: o nome precisa ser exatamente esse.  
> Se o shortcode for escrito de forma diferente, ele será exibido como texto na página.

---

## 5. Como inserir na página do WordPress

### 5.1 Abrir a página

1. Vá em **Páginas → Todas as páginas**
2. Clique em **Editar** na página desejada

### 5.2 Usar o Gutenberg

Como o site usa o editor em blocos, faça assim:

1. Clique no botão **+**
2. Procure por **Shortcode**
3. Insira o bloco **Shortcode**
4. Cole o shortcode desejado
5. Clique em **Atualizar**

---

## 6. Exemplos de uso do shortcode

### 6.1 Exibir todas as comissões

```text
[ime_comissoes]
```

Esse formato exibe todas as comissões disponíveis.

---

### 6.2 Exibir apenas uma comissão específica

```text
[ime_comissoes id="14"]
```

Use esse formato quando quiser mostrar só uma comissão.

---

### 6.3 Exibir várias comissões em uma ordem específica

```text
[ime_comissoes ids="13,14,15,16"]
```

Isso é útil quando você quer montar blocos diferentes na mesma página e controlar a ordem manualmente.

---

### 6.4 Exibir por categoria/tipo

```text
[ime_comissoes tipo="conselhos-departamento"]
```

Exemplos de categorias possíveis:

- `orgaos-colegiados`
- `conselhos-departamento`
- `cursos-graduacao`
- `programas-posgraduacao`
- `mais-comissoes`

---

## 7. Como organizar a página em blocos

Se você quiser montar a página com seções separadas, a forma mais prática é usar:

- **Um bloco de Título**
- **Um bloco Shortcode abaixo**
- Repetir para cada grupo de comissões

### Exemplo de estrutura

#### Órgãos Colegiados
```text
[ime_comissoes tipo="orgaos-colegiados"]
```

#### Conselhos de Departamento
```text
[ime_comissoes tipo="conselhos-departamento"]
```

#### Comissões de Graduação
```text
[ime_comissoes tipo="cursos-graduacao"]
```

#### Pós-Graduação
```text
[ime_comissoes tipo="programas-posgraduacao"]
```

#### Mais Comissões
```text
[ime_comissoes tipo="mais-comissoes"]
```

---

## 8. Ordenação dos blocos

Se você quiser mudar a ordem de exibição:

- Basta **arrastar os blocos** no Gutenberg
- Ou editar a página e reorganizar os blocos manualmente
- Para listas específicas, use o parâmetro `ids` na ordem desejada

### Exemplo

Se quiser mostrar primeiro a comissão 14, depois a 7 e depois a 22:

```text
[ime_comissoes ids="14,7,22"]
```

---

## 9. Como funciona o conteúdo exibido

Cada comissão carregada na página pode conter:

- **Título da comissão**
- **Seções internas**
  - Titulares
  - Suplentes
  - Representantes
  - Cargos específicos
- **Membros**
- **Início do mandato**
- **Fim do mandato**

Quando a página externa da USP tiver essa separação, o sistema tenta preservar essa estrutura na exibição do WordPress.

---

## 10. Botão de PDF

Cada comissão pode exibir um botão para impressão/salvamento em PDF.

### Como usar

1. Abra a comissão desejada
2. Clique no botão **Salvar em PDF**
3. Use a impressão do navegador para salvar o documento

O layout de impressão foi preparado para mostrar apenas o conteúdo da comissão, sem elementos do tema do WordPress.

---

## 11. Atualização dos dados

Os dados são atualizados de duas formas:

- **Automática**, em horário agendado de madrugada
- **Manual**, quando alguém força a atualização

Isso permite manter a página sempre atualizada sem depender de edição manual no WordPress.

---

## 12. Troca de ambiente

Se o site estiver em:

- **homologação**
- **produção**

é preciso verificar a URL base da API no shortcode.

### Exemplo de configuração

No código do shortcode, a URL pode ser algo como:

```text
http://www2.ime.usp.br:8020/api
```

Se mudar o servidor, essa URL deve ser atualizada.

---

## 13. Problemas comuns

### 13.1 O shortcode aparece como texto na página

Exemplo:

```text
[ime_comissoes id="14"]
```

Se isso aparecer escrito na página, verifique:

- se o shortcode está ativo
- se o nome está correto
- se foi inserido no bloco **Shortcode**
- se as aspas são normais, e não aspas curvas

Use sempre:

```text
[ime_comissoes id="14"]
```

e não:

```text
[ime_comissoes id=”14”]
```

---

### 13.2 A página não carrega os dados

Verifique:

- se o serviço Python está rodando
- se a porta **8020** está liberada
- se a URL da API está correta
- se o servidor está acessível a partir do WordPress

---

### 13.3 A comissão aparece, mas sem dados

Isso pode acontecer se:

- a URL da comissão externa mudou
- houve erro no scraping
- a página externa da USP não carregou corretamente

Nesse caso, o sistema deve tentar usar o cache ou refazer a coleta.

---

### 13.4 O shortcode mostra todas as comissões mesmo com `id` ou `tipo`

Isso significa que o shortcode PHP ou a API ainda não estão filtrando corretamente.

Verifique se:

- o shortcode PHP está lendo os parâmetros `id`, `ids` e `tipo`
- a API aceita filtros na rota correspondente
- o deploy foi atualizado no servidor
- o cache do navegador ou do WordPress foi limpo

---

## 14. Boas práticas de uso

- Use **um bloco por seção**
- Prefira `tipo` para páginas maiores
- Use `id` para páginas específicas
- Use `ids` quando quiser controlar exatamente a ordem
- Evite copiar shortcode com aspas erradas
- Sempre revise a página após atualizar

---

## 15. Fluxo recomendado para criação de páginas no WordPress

### Página principal de colegiados

Use:

```text
[ime_comissoes]
```

### Página por categoria

Exemplos:

```text
[ime_comissoes tipo="orgaos-colegiados"]
[ime_comissoes tipo="conselhos-departamento"]
[ime_comissoes tipo="cursos-graduacao"]
[ime_comissoes tipo="programas-posgraduacao"]
[ime_comissoes tipo="mais-comissoes"]
```

### Página específica de uma comissão

Exemplo:

```text
[ime_comissoes id="14"]
```

### Página com seleção manual e ordem personalizada

Exemplo:

```text
[ime_comissoes ids="14,7,22"]
```

---

## 16. Sugestão de estrutura da página no WordPress

Uma organização simples e eficiente seria:

- Título da página
- Texto introdutório
- Bloco de seção:
  - Título da seção
  - Shortcode correspondente
- Repetir para cada grupo
- Texto final ou observação
- Salvar a página

---

## 17. Resumo rápido dos shortcodes

| Objetivo | Shortcode |
|---|---|
| Todas as comissões | `[ime_comissoes]` |
| Uma comissão | `[ime_comissoes id="14"]` |
| Várias comissões | `[ime_comissoes ids="13,14,15"]` |
| Por categoria | `[ime_comissoes tipo="conselhos-departamento"]` |

---

## 18. Checklist de publicação

Antes de publicar a página, confirme:

- [ ] O shortcode está no bloco correto
- [ ] O nome do shortcode está correto
- [ ] A API está respondendo
- [ ] O conteúdo está aparecendo corretamente
- [ ] O accordion abre e fecha
- [ ] O botão PDF aparece
- [ ] O layout não quebrou o tema

---

## 19. Observações finais

Este sistema foi criado para eliminar o processo manual de:

- acessar várias páginas externas
- copiar informações em planilhas
- gerar PDFs manualmente
- fazer upload manual no WordPress

Agora a manutenção é centralizada na API e a exibição no WordPress fica mais simples, rápida e organizada.

Se houver atualização na estrutura das páginas externas da USP, pode ser necessário ajustar o scraper.