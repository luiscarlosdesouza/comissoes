import os
import asyncio
from fastapi import APIRouter, Depends, Request, Form, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.scraper import update_all_comissoes, scrape_comissao

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminusp")

def check_auth(request: Request):
    """Verifica autenticação via Cookie (simples)."""
    return request.cookies.get("session") == "authenticated"

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session", value="authenticated", httponly=True)
        return response
    
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Credenciais inválidas"})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    comissoes = db.query(models.Comissao).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "comissoes": comissoes
    })

@router.post("/comissao/add")
async def add_comissao(request: Request, nome: str = Form(...), url: str = Form(...), db: Session = Depends(get_db)):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
    nova_comissao = models.Comissao(nome=nome, url=url)
    db.add(nova_comissao)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/comissao/delete/{comissao_id}")
async def delete_comissao(request: Request, comissao_id: int, db: Session = Depends(get_db)):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
    comissao = db.query(models.Comissao).filter(models.Comissao.id == comissao_id).first()
    if comissao:
        db.delete(comissao)
        db.commit()
        
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/force_update_all")
async def force_update_all(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Aciona a atualização de TODAS as comissões no Background para não travar a UI."""
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
    # Agendamos na background task do FastAPI o update geral
    loop = asyncio.get_event_loop()
    loop.create_task(update_all_comissoes(db))
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "comissoes": db.query(models.Comissao).all(),
        "message": "Atualização geral iniciada em background! Isso pode demorar alguns minutos."
    })

@router.post("/force_update_single/{comissao_id}")
async def force_update_single(request: Request, comissao_id: int, db: Session = Depends(get_db)):
    """Atualiza de forma síncrona/espera uma única comissão, ou manda pra background se preferir."""
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    comissao = db.query(models.Comissao).filter(models.Comissao.id == comissao_id).first()
    
    if comissao:
        # Para evitar travar a UI por mto tempo, mandamos essa task específica pro loop
        async def update_single():
            from datetime import datetime
            data_json = await scrape_comissao(comissao.url)
            if data_json.get("secoes"):
                db.query(models.Membro).filter(models.Membro.comissao_id == comissao.id).delete()
                for secao in data_json["secoes"]:
                    categoria = secao.get("nome", "Geral")
                    for m in secao.get("membros", []):
                        periodo_str = f"{m.get('inicio_mandato', '')} - {m.get('fim_mandato', '')}".strip(" -")
                        novo_membro = models.Membro(comissao_id=comissao.id, nome=m.get("nome", ""), cargo=categoria, periodo=periodo_str)
                        db.add(novo_membro)
                comissao.data_atualizacao = datetime.utcnow()
                db.commit()
                
        loop = asyncio.get_event_loop()
        loop.create_task(update_single())

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "comissoes": db.query(models.Comissao).all(),
        "message": f"Atualização da comissão {comissao.nome} iniciada em background."
    })
