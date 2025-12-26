from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, crud
from app.database import get_db
from app.routers.auth import get_current_user


router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def root_redirect():
    return RedirectResponse(url="/login")

@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    total_familles = db.query(models.Famille).count()
    total_membres = db.query(models.Membre).count()
    libreville_membres = db.query(models.Membre).filter(models.Membre.city.ilike("libreville")).count()

    doublons_groupes = (
        db.query(
            func.lower(models.Membre.first_name),
            func.lower(models.Membre.last_name),
            models.Membre.date_of_birth
        )
        .group_by(
            func.lower(models.Membre.first_name),
            func.lower(models.Membre.last_name),
            models.Membre.date_of_birth
        )
        .having(func.count(models.Membre.id) > 1)
        .all()
    )

    stats = {
        "total_familles": total_familles,
        "total_membres": total_membres,
        "libreville_membres": libreville_membres,
        "total_doublons": len(doublons_groupes)
    }

    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})

@router.get("/page-familles", response_class=HTMLResponse)
def page_familles(request: Request, db: Session = Depends(get_db)):
    familles = crud.list_familles(db)
    return templates.TemplateResponse("familles.html", {"request": request, "familles": familles})

@router.get("/page-utilisateurs", response_class=HTMLResponse)
def page_utilisateurs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    utilisateurs = db.query(models.Utilisateur).all()
    return templates.TemplateResponse("utilisateurs.html", {
        "request": request, 
        "utilisateurs": utilisateurs,
        "current_user": current_user
    })


@router.get("/page-stats", response_class=HTMLResponse)
def page_stats(request: Request, db: Session = Depends(get_db)):
    stats_globales = {
        "total_familles": db.query(models.Famille).count(),
        "total_membres": db.query(models.Membre).count()
    }
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats_globales})

@router.get("/page-famille-edit", response_class=HTMLResponse)
def page_famille_edit(request: Request):
    return templates.TemplateResponse("famille_edit.html", {"request": request})

@router.get("/home", response_class=HTMLResponse)
def home_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    total_familles = db.query(models.Famille).count()
    total_membres = db.query(models.Membre).count()
    libreville_membres = db.query(models.Membre).filter(models.Membre.city.ilike("libreville")).count()

    doublons_groupes = (
        db.query(
            func.lower(models.Membre.first_name),
            func.lower(models.Membre.last_name),
            models.Membre.date_of_birth
        )
        .group_by(
            func.lower(models.Membre.first_name),
            func.lower(models.Membre.last_name),
            models.Membre.date_of_birth
        )
        .having(func.count(models.Membre.id) > 1)
        .all()
    )

    stats = {
        "total_familles": total_familles,
        "total_membres": total_membres,
        "libreville_membres": libreville_membres,
        "total_doublons": len(doublons_groupes)
    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "user": current_user  # 👈 Ajout ici
    })
