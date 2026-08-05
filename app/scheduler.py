from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scraper import update_all_comissoes
from app.database import SessionLocal
import logging
import asyncio

logger = logging.getLogger(__name__)

import os

tz = os.getenv("TZ", "UTC")
scheduler = AsyncIOScheduler(timezone=tz)

async def run_scraper_job():
    """Roda a rotina asíncrona de atualização no Scheduler de madrugada."""
    logger.info("Iniciando rotina agendada (Madrugada) de atualização de comissões...")
    db = SessionLocal()
    try:
        await update_all_comissoes(db)
    except Exception as e:
        logger.error(f"Erro na rotina de atualização noturna: {e}")
    finally:
        db.close()

def start_scheduler():
    # Roda todos os dias às 03:00 da manhã
    scheduler.add_job(run_scraper_job, 'cron', hour=3, minute=0)
    scheduler.start()
    logger.info("Scheduler iniciado. Scraper agendado para rodar diariamente às 03:00 AM.")
