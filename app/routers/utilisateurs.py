from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.routers import auth
from app.routers.auth import get_current_user

# --- Initialisation du router ---
router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])
templates = Jinja2Templates(directory="app/templates")


# --- Page HTML des utilisateurs ---
from sqlalchemy.orm import joinedload

@router.get("/", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def page_utilisateurs(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    if current_user.role not in ["super_admin", "superviseur_provincial"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    query = db.query(models.Utilisateur).options(joinedload(models.Utilisateur.province))

    if current_user.role == "super_admin":
        utilisateurs = query.join(models.Province).order_by(models.Province.nom).all()
    else:
        utilisateurs = query.filter(models.Utilisateur.province_id == current_user.province_id)\
                            .join(models.Province)\
                            .order_by(models.Province.nom)\
                            .all()

    provinces = db.query(models.Province).all()
    return templates.TemplateResponse("utilisateurs.html", {
        "request": request,
        "utilisateurs": utilisateurs,
        "provinces": provinces,
        "current_user": current_user
    })


# --- Création d'un utilisateur via formulaire HTML ---
@router.post("/", response_class=HTMLResponse)
def create_utilisateur_html(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    province_id: int = Form(...),
    db: Session = Depends(database.get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    if current_user.role != "super_admin" and province_id != current_user.province_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez créer que dans votre province")

    existing_user = db.query(models.Utilisateur).filter(models.Utilisateur.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    hashed_password = auth.get_password_hash(password)

    db_user = models.Utilisateur(
        username=username,
        hashed_password=hashed_password,
        role=role,
        province_id=province_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return RedirectResponse("/utilisateurs", status_code=303)


# --- Création d'un utilisateur (JSON API) ---
@router.post("/json", response_model=schemas.UtilisateurResponse)
def create_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.Utilisateur).filter(models.Utilisateur.username == utilisateur.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    hashed_password = auth.get_password_hash(utilisateur.password)

    db_user = models.Utilisateur(
        username=utilisateur.username,
        hashed_password=hashed_password,
        role=utilisateur.role,
        province_id=utilisateur.province_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Liste des utilisateurs (JSON API) ---
@router.get("/json", response_model=list[schemas.UtilisateurResponse])
def get_utilisateurs(db: Session = Depends(database.get_db)):
    return db.query(models.Utilisateur).all()


# --- Récupérer un utilisateur par ID ---
@router.get("/{user_id}", response_model=schemas.UtilisateurResponse)
def get_utilisateur(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user


# --- Supprimer un utilisateur via formulaire HTML ---
@router.post("/{user_id}/delete", response_class=HTMLResponse)
def delete_utilisateur_html(request: Request, user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(db_user)
    db.commit()

    return RedirectResponse("/utilisateurs", status_code=303)


# --- Supprimer un utilisateur (JSON API) ---
@router.delete("/{user_id}")
def delete_utilisateur(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé"}
