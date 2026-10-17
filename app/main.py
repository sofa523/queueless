from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from .database import init_db
from .routers import admin, client, pages
from .repositories import ticket_repo
from .config import TICKET_TTL_HOURS

app = FastAPI(title="QueueLess", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router)
app.include_router(admin.router)
app.include_router(client.router)


@app.on_event("startup")
def startup():
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: ticket_repo.cleanup_expired(TICKET_TTL_HOURS),
                      "interval", hours=1)
    scheduler.start()


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500,
                        content={"error": {"code": "INTERNAL_ERROR",
                                           "message": "Внутренняя ошибка сервера"}})