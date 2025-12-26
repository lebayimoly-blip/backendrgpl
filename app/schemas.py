from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- Membres ---
class MembreBase(BaseModel):
    first_name: str
    last_name: str
    role: Optional[str] = None

    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    place_of_birth: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None


class MembreCreate(MembreBase):
    pass


class Membre(MembreBase):
    id: int

    class Config:
        from_attributes = True


class MembreResponse(MembreBase):
    id: int

    class Config:
        orm_mode = True   # ✅ indispensable pour SQLAlchemy → Pydantic


# --- Familles ---
class FamilleBase(BaseModel):
    name: str

    # Champs racine
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    place_of_birth: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

    # Champs génériques
    localisation: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_path: Optional[str] = None
    duree_remplissage: Optional[int] = None


class FamilleCreate(FamilleBase):
    membres: List[MembreCreate] = []


class Famille(FamilleBase):
    id: int
    created_at: datetime.datetime
    membres: List[Membre] = []

    class Config:
        from_attributes = True


class FamilleResponse(FamilleBase):
    id: int
    created_at: datetime.datetime
    membres: List[MembreResponse] = []

    class Config:
        orm_mode = True


# --- Utilisateurs ---
class UtilisateurBase(BaseModel):
    username: str
    role: str


class UtilisateurCreate(UtilisateurBase):
    password: str


class Utilisateur(UtilisateurBase):
    id: int

    class Config:
        from_attributes = True


class UtilisateurResponse(UtilisateurBase):
    id: int

    class Config:
        orm_mode = True


# --- Localisation & Durée ---
class LocalisationCreate(BaseModel):
    latitude: float
    longitude: float


class DureeCreate(BaseModel):
    duree_remplissage: int
