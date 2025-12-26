# app/routers/offline.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/add-membre", response_class=HTMLResponse)
async def add_membre(request: Request):
    return templates.TemplateResponse("add_membre.html", {"request": request})

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.get("/edit-famille", response_class=HTMLResponse)
async def edit_famille(request: Request):
    return templates.TemplateResponse("edit_famille.html", {"request": request})

@router.get("/familles", response_class=HTMLResponse)
async def familles(request: Request):
    return templates.TemplateResponse("familles.html", {"request": request})

@router.get("/famille-detail", response_class=HTMLResponse)
async def famille_detail(request: Request):
    return templates.TemplateResponse("famille_detail.html", {"request": request})

@router.get("/famille-edit", response_class=HTMLResponse)
async def famille_edit(request: Request):
    return templates.TemplateResponse("famille_edit.html", {"request": request})

@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/offline.html", response_class=HTMLResponse)
async def offline(request: Request):
    return templates.TemplateResponse("offline.html", {"request": request})

@router.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})

@router.get("/synchronisation", response_class=HTMLResponse)
async def synchronisation(request: Request):
    return templates.TemplateResponse("synchronisation.html", {"request": request})

@router.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})

@router.get("/utilisateurs", response_class=HTMLResponse)
async def utilisateurs(request: Request):
    return templates.TemplateResponse("utilisateurs.html", {"request": request})

@router.get("/zones-attribuees", response_class=HTMLResponse)
async def zones_attribuees(request: Request):
    return templates.TemplateResponse("zones_attribuees.html", {"request": request})

@router.get("/zone-travail", response_class=HTMLResponse)
async def zone_travail(request: Request):
    return templates.TemplateResponse("zone_travail.html", {"request": request})
