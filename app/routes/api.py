from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/comissoes/html", response_class=HTMLResponse)
async def get_comissoes_html(request: Request, db: Session = Depends(get_db)):
    """Retorna o HTML formatado para ser injetado no WordPress"""
    comissoes = db.query(models.Comissao).all()
    return templates.TemplateResponse("public/comissao.html", {
        "request": request,
        "comissoes": comissoes
    })

@router.get("/comissoes", response_class=JSONResponse)
async def list_comissoes_json(db: Session = Depends(get_db)):
    """Retorna a lista de comissões em formato JSON"""
    comissoes = db.query(models.Comissao).all()
    resultado = []
    
    for c in comissoes:
        membros = [{"nome": m.nome, "cargo": m.cargo, "periodo": m.periodo} for m in c.membros]
        resultado.append({
            "id": c.id,
            "nome": c.nome,
            "url": c.url,
            "data_atualizacao": c.data_atualizacao.isoformat() if c.data_atualizacao else None,
            "membros": membros
        })
        
    return JSONResponse(content=resultado)
