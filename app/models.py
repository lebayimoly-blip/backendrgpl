from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Famille(Base):
    __tablename__ = "familles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Champs enrichis pour la personne racine
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    id_type = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    place_of_birth = Column(String, nullable=True)
    province = Column(String, nullable=True)
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)

    # Champs génériques
    localisation = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo_path = Column(String, nullable=True)
    duree_remplissage = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)

    created_by = relationship("Utilisateur", back_populates="familles")
    membres = relationship("Membre", back_populates="famille")
    


class Membre(Base):
    __tablename__ = "membres"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String, nullable=True)

    # Nouveaux champs
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    id_type = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    place_of_birth = Column(String, nullable=True)
    province = Column(String, nullable=True)
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)

    famille_id = Column(Integer, ForeignKey("familles.id"))
    famille = relationship("Famille", back_populates="membres")


from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)

    # Relations
    province = relationship("Province", back_populates="utilisateurs")
    familles = relationship("Famille", back_populates="created_by")
    zones = relationship("Zone", back_populates="utilisateur")


class Province(Base):
    __tablename__ = "provinces"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)

    utilisateurs = relationship("Utilisateur", back_populates="province") 

from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    geometrie = Column(JSON, nullable=False)  # Stocke le GeoJSON

    utilisateur = relationship("Utilisateur", back_populates="zones")
