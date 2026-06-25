import csv
import os
import sys

# Ajusta o path para conseguir importar do pacote app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Comissao

def classificar_comissao(nome, url):
    nome_up = (nome or "").upper()
    url_up = (url or "").upper()
    
    # orgaos-colegiados
    if "(CCEX)" in nome_up or "CCEX" in url_up: return "orgaos-colegiados"
    if "(CG)" in nome_up or "/CG?" in url_up: return "orgaos-colegiados"
    if "CONGREG" in nome_up or "CONGREG" in url_up: return "orgaos-colegiados"
    if "(CPG)" in nome_up or "/CPG?" in url_up: return "orgaos-colegiados"
    if "(CTA)" in nome_up or "/CTA?" in url_up: return "orgaos-colegiados"
    if "(CRINT)" in nome_up or "CRINT" in url_up: return "orgaos-colegiados"
    if "(CPQI)" in nome_up or "CPQ" in url_up: return "orgaos-colegiados"
    if "(CIPA)" in nome_up or "CIPA" in url_up: return "orgaos-colegiados"
    if "(CIP)" in nome_up or "/CIP?" in url_up: return "orgaos-colegiados"
    if "BIBLIOTECA" in nome_up: return "orgaos-colegiados"
    
    # conselhos-departamento
    if "- MAC" in nome_up or ("COMPUTA" in nome_up and "DEPARTAMENTO" in nome_up): return "conselhos-departamento"
    if "- MAE" in nome_up or ("ESTAT" in nome_up and "DEPARTAMENTO" in nome_up): return "conselhos-departamento"
    if "- MAP" in nome_up or ("APLICADA" in nome_up and "DEPARTAMENTO" in nome_up): return "conselhos-departamento"
    if "- MAT" in nome_up or "DEPARTAMENTO DE MATEM" in nome_up: return "conselhos-departamento"
    
    # cursos-graduacao
    if "(COC)" in nome_up: return "cursos-graduacao"
    
    # programas-posgraduacao
    if "(CCP)" in nome_up: return "programas-posgraduacao"
    
    # fallback
    return "mais-comissoes"

def seed_db():
    # Cria as tabelas se não existirem
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkspublicos.csv")
    
    if not os.path.exists(csv_path):
        print(f"ERRO: Arquivo {csv_path} não encontrado.")
        print("Por favor, verifique se o arquivo 'linkspublicos.csv' está na pasta 'app/' e tente novamente.")
        return

    db = SessionLocal()
    
    try:
        print(f"Lendo dados de {csv_path}...")
        # Usa encoding latin-1 (ou iso-8859-1) para corrigir caracteres como 
        with open(csv_path, mode="r", encoding="latin-1") as file:
            # Informa o delimitador ponto e vírgula
            reader = csv.DictReader(file, delimiter=";")
            
            count = 0
            for row in reader:
                colegiado = row.get("colegiado")
                link = row.get("link")
                
                if colegiado and link:
                    # Verifica se já existe para não duplicar
                    existente = db.query(Comissao).filter(Comissao.url == link).first()
                    
                    categoria = classificar_comissao(colegiado, link)
                    
                    if not existente:
                        nova_comissao = Comissao(nome=colegiado, url=link, categoria=categoria)
                        db.add(nova_comissao)
                        count += 1
                    else:
                        # Atualiza a categoria das comissões existentes
                        if existente.categoria != categoria:
                            existente.categoria = categoria
                        
        db.commit()
        print(f"Sucesso! Foram processados/inseridos registros. {count} novos adicionados.")
        
    except Exception as e:
        print(f"Erro durante a importação: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
