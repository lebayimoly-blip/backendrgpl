from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from .. import database, models

router = APIRouter(prefix="/stats", tags=["statistiques"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/page-stats", response_class=HTMLResponse)
def page_stats(
    request: Request,
    db: Session = Depends(database.get_db),
    annee: int = None,
    depuis: int = None
):
    base_query = db.query(models.Membre)

    if annee:
        base_query = base_query.filter(func.substr(models.Membre.date_of_birth, 1, 4) == str(annee))
    elif depuis:
        annee_min = datetime.now().year - depuis
        base_query = base_query.filter(func.substr(models.Membre.date_of_birth, 1, 4) >= str(annee_min))

    total_familles = db.query(models.Famille).count()
    total_membres = base_query.count()

    genres = dict(
        base_query
        .with_entities(models.Membre.gender, func.count())
        .filter(models.Membre.gender.isnot(None), models.Membre.gender != '')
        .group_by(models.Membre.gender)
        .all()
    )

    provinces = dict(
        base_query
        .with_entities(models.Membre.province, func.count())
        .filter(models.Membre.province.isnot(None), models.Membre.province != '')
        .group_by(models.Membre.province)
        .all()
    )

    roles = dict(
        base_query
        .with_entities(models.Membre.role, func.count())
        .filter(models.Membre.role.isnot(None), models.Membre.role != '')
        .group_by(models.Membre.role)
        .all()
    )

    villes = dict(
        base_query
        .with_entities(models.Membre.city, func.count())
        .filter(models.Membre.city.isnot(None), models.Membre.city != '')
        .group_by(models.Membre.city)
        .all()
    )

    naissances = dict(
        base_query
        .with_entities(func.substr(models.Membre.date_of_birth, 1, 4), func.count())
        .filter(models.Membre.date_of_birth.like("____-%"))
        .group_by(func.substr(models.Membre.date_of_birth, 1, 4))
        .order_by(func.substr(models.Membre.date_of_birth, 1, 4))
        .all()
    )

    stats = {
        "total_familles": total_familles,
        "total_membres": total_membres,
        "genres": genres,
        "provinces": provinces,
        "roles": roles,
        "villes": villes,
        "naissances": naissances,
        "filtre_annee": annee,
        "filtre_depuis": depuis
    }

    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats})
