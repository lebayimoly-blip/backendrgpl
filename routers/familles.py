import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.routers import auth
from app.utils.files import UPLOAD_DIR, generate_family_filename
from app.database import get_db

router = APIRouter(prefix="/familles", tags=["familles"])
templates = Jinja2Templates(directory="app/templates")


# --- Liste des familles (HTML) ---
from sqlalchemy.orm import joinedload

@router.get("/", response_class=HTMLResponse)
def page_familles(request: Request, db: Session = Depends(database.get_db)):
    familles = db.query(models.Famille).options(joinedload(models.Famille.created_by)).all()
    return templates.TemplateResponse("familles.html", {
        "request": request,
        "familles": familles
    })

# --- Page de création de famille (utilise famille_edit.html déjà existant) ---
@router.get("/create", response_class=HTMLResponse)
def page_create_famille(request: Request):
    return templates.TemplateResponse("famille_edit.html", {"request": request})


# --- Création d'une famille ---
@router.post("/", response_model=schemas.FamilleResponse)
async def create_famille(
    name: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    id_type: str = Form(...),
    id_number: str = Form(...),
    place_of_birth: str = Form(...),
    province: str = Form(...),
    city: str = Form(...),
    district: str = Form(...),
    duree_remplissage: int = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_user),
):
    db_famille = models.Famille(
        name=name,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender,
        nationality=nationality,
        id_type=id_type,
        id_number=id_number,
        place_of_birth=place_of_birth,
        province=province,
        city=city,
        district=district,
        duree_remplissage=duree_remplissage,
        latitude=latitude,
        longitude=longitude,
        created_by_id=current_user.id,
    )
    db.add(db_famille)
    db.commit()
    db.refresh(db_famille)

    # ✅ Ajouter la personne racine comme membre (Personne cible)
    db_membre_racine = models.Membre(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender,
        nationality=nationality,
        id_type=id_type,
        id_number=id_number,
        place_of_birth=place_of_birth,
        province=province,
        city=city,
        district=district,
        role="Personne cible",
        famille_id=db_famille.id
    )
    db.add(db_membre_racine)
    db.commit()

    if photo:
        filename = generate_family_filename(db_famille.id, photo.filename)
        photo_path = os.path.join(UPLOAD_DIR, filename)
        with open(photo_path, "wb") as buffer:
            buffer.write(await photo.read())
        db_famille.photo_path = filename
        db.commit()
        db.refresh(db_famille)

    return db_famille

# --- Ajout d'un membre à une famille ---
@router.post("/{famille_id}/members", response_model=schemas.MembreResponse)
def add_member(famille_id: int, membre: schemas.MembreCreate, db: Session = Depends(database.get_db)):
    db_famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    db_membre = models.Membre(**membre.dict(), famille_id=famille_id)
    db.add(db_membre)
    db.commit()
    db.refresh(db_membre)
    return db_membre


# --- Liste des membres d'une famille ---
@router.get("/{famille_id}/members", response_model=list[schemas.MembreResponse])
def list_members(famille_id: int, db: Session = Depends(database.get_db)):
    db_famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")
    return db_famille.membres


# --- Supprimer un membre d'une famille ---
@router.delete("/{famille_id}/members/{membre_id}")
def delete_member(famille_id: int, membre_id: int, db: Session = Depends(database.get_db)):
    db_membre = db.query(models.Membre).filter(
        models.Membre.id == membre_id,
        models.Membre.famille_id == famille_id
    ).first()
    if not db_membre:
        raise HTTPException(status_code=404, detail="Membre non trouvé")

    db.delete(db_membre)
    db.commit()
    return {"message": "Membre supprimé"}


# --- Mise à jour de la localisation ---
@router.post("/{famille_id}/localisation")
def update_localisation(famille_id: int, localisation: schemas.LocalisationCreate, db: Session = Depends(database.get_db)):
    db_famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    db_famille.latitude = localisation.latitude
    db_famille.longitude = localisation.longitude
    db.commit()
    return {"message": "Localisation mise à jour"}


# --- Mise à jour de la durée de remplissage ---
@router.post("/{famille_id}/duree")
def update_duree(famille_id: int, duree: schemas.DureeCreate, db: Session = Depends(database.get_db)):
    db_famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    db_famille.duree_remplissage = duree.duree_remplissage
    db.commit()
    return {"message": "Durée de remplissage enregistrée"}

@router.get("/{famille_id}", response_class=HTMLResponse)
def voir_famille(famille_id: int, request: Request, db: Session = Depends(get_db)):
    famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")
    return templates.TemplateResponse("famille_detail.html", {"request": request, "famille": famille})

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

@router.get("/{famille_id}/edit", response_class=HTMLResponse)
def edit_famille(famille_id: int, request: Request, db: Session = Depends(get_db)):
    famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    membres = db.query(models.Membre).filter(models.Membre.famille_id == famille_id).all()

    return templates.TemplateResponse("edit_famille.html", {
        "request": request,
        "famille": famille,
        "membres": membres
    })

@router.post("/{famille_id}/update") 
async def update_famille(famille_id: int, request: Request, db: Session = Depends(get_db)): 
    form = await request.form()
    famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    famille.nom = form.get("name")
    # ... mets à jour les autres champs

    db.commit()
    return RedirectResponse(url="/page-familles", status_code=303)

from fastapi import Form

@router.get("/{famille_id}/members/add", response_class=HTMLResponse)
def add_membre_form(famille_id: int, request: Request, db: Session = Depends(get_db)):
    famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    return templates.TemplateResponse("add_membre.html", {
        "request": request,
        "famille": famille
    })

from fastapi.responses import RedirectResponse

@router.post("/{famille_id}/members/form")
async def add_member_form_post(
    famille_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()

    db_famille = db.query(models.Famille).filter(models.Famille.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille non trouvée")

    membre = models.Membre(
        first_name=form.get("first_name"),
        last_name=form.get("last_name"),
        role=form.get("role"),
        date_of_birth=form.get("date_of_birth"),
        gender=form.get("gender"),
        nationality=form.get("nationality"),
        id_type=form.get("id_type"),
        id_number=form.get("id_number"),
        place_of_birth=form.get("place_of_birth"),
        province=form.get("province"),
        city=form.get("city"),
        district=form.get("district"),
        famille_id=famille_id
    )

    db.add(membre)
    db.commit()

    return RedirectResponse(url=f"/familles/{famille_id}/edit", status_code=303)

@router.post("/{famille_id}/members/{membre_id}/update")
async def update_membre(
    famille_id: int,
    membre_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()

    membre = db.query(models.Membre).filter(
        models.Membre.id == membre_id,
        models.Membre.famille_id == famille_id
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Membre non trouvé")

    membre.first_name = form.get("first_name")
    membre.last_name = form.get("last_name")
    membre.role = form.get("role")
    membre.date_of_birth = form.get("date_of_birth")
    membre.gender = form.get("gender")
    membre.nationality = form.get("nationality")
    membre.id_type = form.get("id_type")
    membre.id_number = form.get("id_number")
    membre.place_of_birth = form.get("place_of_birth")
    membre.province = form.get("province")
    membre.city = form.get("city")
    membre.district = form.get("district")

    db.commit()

    return RedirectResponse(url=f"/familles/{famille_id}/edit", status_code=303)
