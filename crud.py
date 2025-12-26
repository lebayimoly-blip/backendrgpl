from sqlalchemy.orm import Session
from app import models, schemas
from app.security import get_password_hash
from app.security import verify_password

# --- Utilisateurs ---
def create_utilisateur(db: Session, utilisateur: schemas.UtilisateurCreate):
    # Vérifie si l'utilisateur existe déjà
    existing_user = db.query(models.Utilisateur).filter(
        models.Utilisateur.username == utilisateur.username
    ).first()
    if existing_user:
        return None

    hashed_password = get_password_hash(utilisateur.password)
    db_user = models.Utilisateur(
        username=utilisateur.username,
        hashed_password=hashed_password,
        role=utilisateur.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_utilisateurs(db: Session):
    return db.query(models.Utilisateur).all()


def get_utilisateur_by_id(db: Session, user_id: int):
    return db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()


def delete_utilisateur(db: Session, user_id: int):
    db_user = get_utilisateur_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# --- Familles ---
def create_famille(db: Session, famille: schemas.FamilleCreate, current_user_id: int):
    db_famille = models.Famille(
        name=famille.name,
        first_name=famille.first_name,
        last_name=famille.last_name,
        date_of_birth=famille.date_of_birth,
        gender=famille.gender,
        nationality=famille.nationality,
        id_type=famille.id_type,
        id_number=famille.id_number,
        place_of_birth=famille.place_of_birth,
        province=famille.province,
        city=famille.city,
        district=famille.district,
        duree_remplissage=famille.duree_remplissage,
        latitude=famille.latitude,
        longitude=famille.longitude,
        photo_path=famille.photo_path,
        created_by_id=current_user_id,
    )
    db.add(db_famille)
    db.commit()
    db.refresh(db_famille)
    return db_famille


def list_familles(db: Session):
    return db.query(models.Famille).all()


def get_famille_by_id(db: Session, famille_id: int):
    return db.query(models.Famille).filter(models.Famille.id == famille_id).first()


def delete_famille(db: Session, famille_id: int):
    db_famille = get_famille_by_id(db, famille_id)
    if db_famille:
        db.delete(db_famille)
        db.commit()
        return True
    return False


# --- Membres ---
def add_member(db: Session, famille_id: int, membre: schemas.MembreCreate):
    db_membre = models.Membre(
        first_name=membre.first_name,
        last_name=membre.last_name,
        role=membre.role,
        date_of_birth=membre.date_of_birth,
        gender=membre.gender,
        nationality=membre.nationality,
        id_type=membre.id_type,
        id_number=membre.id_number,
        place_of_birth=membre.place_of_birth,
        province=membre.province,
        city=membre.city,
        district=membre.district,
        famille_id=famille_id,
    )
    db.add(db_membre)
    db.commit()
    db.refresh(db_membre)
    return db_membre


def list_members(db: Session, famille_id: int):
    return db.query(models.Membre).filter(models.Membre.famille_id == famille_id).all()


def get_member_by_id(db: Session, membre_id: int):
    return db.query(models.Membre).filter(models.Membre.id == membre_id).first()


def delete_member(db: Session, membre_id: int):
    db_membre = get_member_by_id(db, membre_id)
    if db_membre:
        db.delete(db_membre)
        db.commit()
        return True
    return False

from app.security import verify_password  # Assure-toi que ceci est bien importé

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
