from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import database, models
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/doublons", tags=["doublons"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
def afficher_doublons(request: Request, db: Session = Depends(database.get_db)):
    # Trouver les groupes de doublons (même nom + même date de naissance, insensibles à la casse)
    doublons_groupes = (
        db.query(
            func.lower(models.Membre.first_name).label("prenom"),
            func.lower(models.Membre.last_name).label("nom"),
            models.Membre.date_of_birth,
            func.count(models.Membre.id).label("nb")
        )
        .group_by(func.lower(models.Membre.first_name), func.lower(models.Membre.last_name), models.Membre.date_of_birth)
        .having(func.count(models.Membre.id) > 1)
        .all()
    )

    # Pour chaque groupe, récupérer les membres concernés
    doublons = []
    for groupe in doublons_groupes:
        membres = db.query(models.Membre).filter(
            func.lower(models.Membre.first_name) == groupe.prenom,
            func.lower(models.Membre.last_name) == groupe.nom,
            models.Membre.date_of_birth == groupe.date_of_birth
        ).all()
        doublons.append({
            "nom": groupe.nom,
            "prenom": groupe.prenom,
            "date_naissance": groupe.date_of_birth,
            "membres": membres
        })

    return templates.TemplateResponse("doublons.html", {"request": request, "doublons": doublons})

@router.post("/supprimer/{membre_id}")
def supprimer_doublon(membre_id: int, db: Session = Depends(database.get_db)):
    membre = db.query(models.Membre).filter(models.Membre.id == membre_id).first()
    if membre:
        db.delete(membre)
        db.commit()
    return RedirectResponse(url="/doublons/", status_code=303)

@router.post("/supprimer-groupe/")
def supprimer_groupe_doublons(
    prenom: str,
    nom: str,
    date_naissance: str,
    db: Session = Depends(database.get_db)
):
    membres = db.query(models.Membre).filter(
        func.lower(models.Membre.first_name) == prenom.lower(),
        func.lower(models.Membre.last_name) == nom.lower(),
        models.Membre.date_of_birth == date_naissance
    ).all()

    # Supprimer tous sauf le premier
    for membre in membres[1:]:
        db.delete(membre)

    db.commit()
    return RedirectResponse(url="/doublons/", status_code=303)





