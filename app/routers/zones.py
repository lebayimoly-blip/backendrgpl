from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import database, models
from app.routers.auth import get_current_user  # utile si tu veux sécuriser certaines routes

router = APIRouter(prefix="/zones", tags=["zones"])
templates = Jinja2Templates(directory="app/templates")

# --- Page HTML pour définir une zone ---
@router.get("/zone-travail", response_class=HTMLResponse)
def definir_zone(request: Request):
    return templates.TemplateResponse("zone_travail.html", {"request": request})

# --- API JSON : recherche dynamique d'utilisateurs ---
@router.get("/recherche-utilisateur", response_class=JSONResponse)
def rechercher_utilisateur(
    q: str = Query(..., min_length=1),
    db: Session = Depends(database.get_db)
):
    utilisateurs = db.query(models.Utilisateur).filter(
        models.Utilisateur.username.ilike(f"%{q}%")
    ).all()

    return [
        {
            "id": u.id,
            "nom": u.username,
            "role": u.role or "rôle non défini"
        }
        for u in utilisateurs
    ]

# --- Page HTML : zones attribuées ---
@router.get("/zones-attribuees", response_class=HTMLResponse)
def afficher_zones_attribuees(
    request: Request,
    utilisateur_id: int | None = Query(None),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Zone).join(models.Utilisateur)
    if utilisateur_id:
        query = query.filter(models.Zone.utilisateur_id == utilisateur_id)

    zones = query.all()
    utilisateurs = db.query(models.Utilisateur).order_by(models.Utilisateur.username).all()

    return templates.TemplateResponse("zones_attribuees.html", {
        "request": request,
        "zones": zones,
        "utilisateurs": utilisateurs,
        "utilisateur_id": utilisateur_id
    })
