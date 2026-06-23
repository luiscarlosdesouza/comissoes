import asyncio
import json
import os
import hashlib
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

CACHE_DIR = os.getenv("CACHE_DIR", "./data/cache_comissoes")
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_filepath(url: str) -> str:
    """Gera um caminho de arquivo de cache baseado no hash da URL."""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")

def save_cache(url: str, data: dict):
    """Salva os dados extraídos no cache local."""
    filepath = _get_cache_filepath(url)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }, f, ensure_ascii=False, indent=2)

def load_cache(url: str) -> dict:
    """Tenta carregar os dados do cache local."""
    filepath = _get_cache_filepath(url)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_content = json.load(f)
                return cache_content.get("data")
        except Exception as e:
            logger.error(f"Erro ao ler cache para {url}: {e}")
    return None

async def _extract_data(page) -> dict:
    """
    Tenta extrair os dados da página Vue.js usando heurísticas flexíveis.
    Como a estrutura pode variar, procuramos por cabeçalhos e tabelas/listas comuns.
    """
    # Exemplo genérico e flexível de extração executado direto no navegador (JavaScript)
    # Isso procura por blocos de conteúdo e tenta estruturar os membros e seções
    
    extraction_script = """
    () => {
        const result = {
            titulo: document.title || '',
            secoes: []
        };
        
        const h1 = document.querySelector('h1, h2, h3, .titulo');
        if (h1) result.titulo = h1.innerText.trim();
        
        // Estrutura real mapeada: seções são delimitadas por div.pb-4 contendo .titulogrupo
        const groups = document.querySelectorAll('.pb-4');
        
        groups.forEach(group => {
            const titleEl = group.querySelector('.titulogrupo');
            if (!titleEl) return;
            
            const secao = {
                nome: titleEl.innerText.trim(),
                membros: []
            };
            
            // Titulares costumam ser .pt-4 e suplentes .pt-2
            const rows = group.querySelectorAll('.pt-4, .pt-2');
            rows.forEach(row => {
                const nameEl = row.querySelector('.w-60');
                const dateEls = row.querySelectorAll('.w-20');
                
                if (nameEl) {
                    let nome = nameEl.innerText.trim();
                    nome = nome.replace(/\\n/g, ' ').replace(/\s+/g, ' ');
                    
                    let cargoFinal = secao.nome;
                    if (nome.includes('- Suplente') || row.querySelector('.suplenteLabel')) {
                        cargoFinal += " (Suplente)";
                        nome = nome.replace('- Suplente', '').trim();
                    } else {
                        cargoFinal += " (Titular)";
                    }
                    
                    let inicio = dateEls.length > 0 ? dateEls[0].innerText.trim() : '';
                    let fim = dateEls.length > 1 ? dateEls[1].innerText.trim() : '';
                    
                    if (nome && nome.length > 3) {
                        secao.membros.push({
                            nome: nome,
                            cargo_real: cargoFinal,
                            inicio_mandato: inicio,
                            fim_mandato: fim
                        });
                    }
                }
            });
            
            if (secao.membros.length > 0) {
                result.secoes.push(secao);
            }
        });
        
        return result;
    }
    """
    
    data = await page.evaluate(extraction_script)
    return data

async def scrape_comissao(url: str, use_cache_on_fail: bool = True) -> dict:
    """
    Abre a página como um browser real, aguarda a renderização, extrai os dados,
    possui retry de 3 tentativas e salva em cache.
    Retorna o JSON padronizado.
    """
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        logger.info(f"Scraping {url} (Tentativa {attempt}/{max_retries})...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = await context.new_page()
                
                # Aguarda até que a rede fique ociosa (networkidle) - Ideal para SPAs (Vue.js)
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Aguarda um elemento chave do Vue ser renderizado (substitua '#app' se necessário)
                # await page.wait_for_selector('#app', timeout=10000)
                
                # Adiciona um pequeno delay para garantir que animações e montagens do Vue finalizaram
                await page.wait_for_timeout(2000) 
                
                extracted_data = await _extract_data(page)
                
                await browser.close()
                
                if extracted_data and extracted_data.get('titulo') or extracted_data.get('secoes'):
                    logger.info(f"Sucesso ao raspar {url}")
                    # Salva no cache
                    save_cache(url, extracted_data)
                    return extracted_data
                else:
                    logger.warning(f"Nenhum dado encontrado na tentativa {attempt}.")
                    
        except PlaywrightTimeoutError:
            logger.error(f"Timeout ao carregar a página {url} na tentativa {attempt}.")
        except Exception as e:
            logger.error(f"Erro inesperado no scraper para {url}: {e}")
            
    # Se chegou aqui, esgotou as tentativas. Tenta retornar do cache local.
    if use_cache_on_fail:
        logger.warning(f"Falha total após {max_retries} tentativas para {url}. Buscando do cache...")
        cached_data = load_cache(url)
        if cached_data:
            logger.info("Retornando dados salvos no cache local.")
            return cached_data
            
    logger.error("Falha no scraping e nenhum dado de cache disponível.")
    return {
        "titulo": "",
        "secoes": []
    }

# Função auxiliar para o update_all_comissoes que será chamado pelo APScheduler / rota administrativa
async def update_all_comissoes(db):
    from . import models
    from datetime import datetime
    
    comissoes = db.query(models.Comissao).all()
    for comissao in comissoes:
        logger.info(f"Atualizando: {comissao.nome} - {comissao.url}")
        
        # Chama a função de scraping
        data_json = await scrape_comissao(comissao.url)
        
        if data_json.get("secoes"):
            # Remove membros antigos
            db.query(models.Membro).filter(models.Membro.comissao_id == comissao.id).delete()
            
            # Insere novos
            for secao in data_json["secoes"]:
                categoria_nome = secao.get("nome", "Geral")
                
                for membro_dict in secao.get("membros", []):
                    periodo_str = f"{membro_dict.get('inicio_mandato', '')} - {membro_dict.get('fim_mandato', '')}".strip(" -")
                    
                    novo_membro = models.Membro(
                        comissao_id=comissao.id,
                        nome=membro_dict.get("nome", ""),
                        cargo=membro_dict.get("cargo_real", categoria_nome),
                        periodo=periodo_str
                    )
                    db.add(novo_membro)
            
            comissao.data_atualizacao = datetime.utcnow()
            db.commit()
            logger.info(f"Comissão {comissao.nome} salva no DB com sucesso.")
