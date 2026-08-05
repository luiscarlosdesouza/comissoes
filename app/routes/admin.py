import os
import asyncio
from fastapi import APIRouter, Depends, Request, Form, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.scraper import update_all_comissoes, scrape_comissao, scrape_progress

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
async def dashboard(request: Request, message: str = None, db: Session = Depends(get_db)):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    comissoes = db.query(models.Comissao).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "comissoes": comissoes,
        "message": message
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
        
    # Agendamos na background task do FastAPI o update geral com sessão isolada
    async def bg_update():
        from app.database import SessionLocal
        bg_db = SessionLocal()
        try:
            await update_all_comissoes(bg_db)
        finally:
            bg_db.close()
            
    loop = asyncio.get_event_loop()
    loop.create_task(bg_update())
    
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
        # Para evitar travar a UI por mto tempo, mandamos essa task específica pro loop com sessão isolada
        async def update_single():
            from datetime import datetime
            from app.database import SessionLocal
            
            bg_db = SessionLocal()
            try:
                # Query a comissão dentro da sessão local do background task
                bg_comissao = bg_db.query(models.Comissao).filter(models.Comissao.id == comissao_id).first()
                if bg_comissao:
                    data_json = await scrape_comissao(bg_comissao.url)
                    if data_json.get("secoes"):
                        bg_db.query(models.Membro).filter(models.Membro.comissao_id == bg_comissao.id).delete()
                        for secao in data_json["secoes"]:
                            categoria = secao.get("nome", "Geral")
                            for m in secao.get("membros", []):
                                periodo_str = f"{m.get('inicio_mandato', '')} - {m.get('fim_mandato', '')}".strip(" -")
                                novo_membro = models.Membro(comissao_id=bg_comissao.id, nome=m.get("nome", ""), cargo=categoria, periodo=periodo_str)
                                bg_db.add(novo_membro)
                        bg_comissao.data_atualizacao = datetime.utcnow()
                        bg_db.commit()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Erro ao atualizar comissão {comissao_id} no background: {e}")
            finally:
                bg_db.close()
                
        loop = asyncio.get_event_loop()
        loop.create_task(update_single())

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "comissoes": db.query(models.Comissao).all(),
        "message": f"Atualização da comissão {comissao.nome} iniciada em background."
    })

@router.get("/comissao/edit/{comissao_id}", response_class=HTMLResponse)
async def edit_comissao_get(request: Request, comissao_id: int, db: Session = Depends(get_db)):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    comissao = db.query(models.Comissao).filter(models.Comissao.id == comissao_id).first()
    if not comissao:
        return RedirectResponse(url="/admin/dashboard?message=Comissao+nao+encontrada", status_code=status.HTTP_302_FOUND)
        
    return templates.TemplateResponse("admin/comissao_edit.html", {
        "request": request,
        "comissao": comissao
    })

@router.post("/comissao/edit/{comissao_id}")
async def edit_comissao_post(
    request: Request, 
    comissao_id: int, 
    nome: str = Form(...), 
    url: str = Form(...), 
    categoria: str = Form(...), 
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
    comissao = db.query(models.Comissao).filter(models.Comissao.id == comissao_id).first()
    if not comissao:
        return RedirectResponse(url="/admin/dashboard?message=Comissao+nao+encontrada", status_code=status.HTTP_302_FOUND)
        
    comissao.nome = nome
    comissao.url = url
    comissao.categoria = categoria
    db.commit()
    
    return RedirectResponse(url=f"/admin/dashboard?message=Comissao+{comissao.nome}+atualizada+com+sucesso", status_code=status.HTTP_302_FOUND)

@router.get("/progress")
def get_progress(request: Request):
    if request.cookies.get("session") != "authenticated":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return JSONResponse(scrape_progress)
