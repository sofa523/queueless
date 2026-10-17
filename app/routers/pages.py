from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index():
    return FileResponse("static/index.html")


@router.get("/admin/{token}", response_class=HTMLResponse)
def admin_page(token: str):
    return FileResponse("static/admin.html")


@router.get("/q/{slug}", response_class=HTMLResponse)
def client_page(slug: str):
    return FileResponse("static/client.html")


@router.get("/sw.js")
def sw():
    return FileResponse("static/sw.js", media_type="application/javascript")