import csv
import os
import sys

# Ajusta o path para conseguir importar do pacote app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Comissao

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
                    if not existente:
                        nova_comissao = Comissao(nome=colegiado, url=link)
                        db.add(nova_comissao)
                        count += 1
                        
        db.commit()
        print(f"Sucesso! Foram inseridos {count} novos registros na tabela 'comissoes'.")
        
    except Exception as e:
        print(f"Erro durante a importação: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
