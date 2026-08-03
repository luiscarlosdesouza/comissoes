from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/comissoes/html", response_class=HTMLResponse)
async def get_comissoes_html(request: Request, ids: str = None, tipo: str = None, layout: str = "acordeon", db: Session = Depends(get_db)):
    """Retorna o HTML formatado para ser injetado no WordPress"""
    query = db.query(models.Comissao)
    
    id_list = []
    if ids:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
        if id_list:
            query = query.filter(models.Comissao.id.in_(id_list))
            
    if tipo:
        query = query.filter(models.Comissao.categoria == tipo.strip())
        
    comissoes = query.all()
    
    # Respeitar a ordem dos IDs passados
    if id_list:
        comissoes.sort(key=lambda x: id_list.index(x.id) if x.id in id_list else 999)
        
    return templates.TemplateResponse("public/comissao.html", {
        "request": request,
        "comissoes": comissoes,
        "layout": layout
    })

@router.get("/comissao/{id}/html", response_class=HTMLResponse)
async def get_comissao_single_html(request: Request, id: int, layout: str = "plano", db: Session = Depends(get_db)):
    """Retorna o HTML formatado para uma única comissão, já expandida"""
    comissao = db.query(models.Comissao).filter(models.Comissao.id == id).first()
    comissoes = [comissao] if comissao else []
    
    return templates.TemplateResponse("public/comissao.html", {
        "request": request,
        "comissoes": comissoes,
        "layout": layout
    })

@router.get("/comissoes", response_class=JSONResponse)
async def list_comissoes_json(ids: str = None, tipo: str = None, db: Session = Depends(get_db)):
    """Retorna a lista de comissões em formato JSON com filtros opcionais"""
    query = db.query(models.Comissao)
    
    if ids:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
        if id_list:
            query = query.filter(models.Comissao.id.in_(id_list))
            
    if tipo:
        query = query.filter(models.Comissao.categoria == tipo.strip())
        
    comissoes = query.all()
    resultado = []
    
    for c in comissoes:
        membros = [{"nome": m.nome, "cargo": m.cargo, "periodo": m.periodo} for m in c.membros]
        resultado.append({
            "id": c.id,
            "nome": c.nome,
            "url": c.url,
            "categoria": c.categoria,
            "data_atualizacao": c.data_atualizacao.isoformat() if c.data_atualizacao else None,
            "membros": membros
        })
        
    return JSONResponse(content=resultado)
