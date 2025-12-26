from fastapi import APIRouter, Request, Form, Depends, Response, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

from app import models, schemas, database
from app import crud

from app.database import get_db

# 🔐 Chargement des variables d'environnement
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 🔐 Création du token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("✅ Token généré :", encoded_jwt)
    return encoded_jwt

# 🔐 Fonction pour récupérer l'utilisateur connecté à partir du cookie
def get_current_user(
    token: str = Cookie(None, alias="access_token"),
    db: Session = Depends(database.get_db)
) -> models.Utilisateur:
    print("🔐 Cookie reçu :", token)

    if not token:
        print("❌ Aucun token trouvé dans le cookie.")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print("📦 Payload décodé :", payload)
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        print("❌ Erreur de décodage JWT :", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.Utilisateur).filter(models.Utilisateur.username == username).first()
    if user is None:
        print("❌ Utilisateur introuvable :", username)
        raise HTTPException(status_code=401, detail="User not found")

    print("✅ Utilisateur authentifié :", user.username)
    return user

# 📦 Configuration du routeur et des templates
router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# 🔐 Page de connexion (GET)
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 🔐 Traitement du formulaire de connexion (POST)
@router.post("/login", response_class=HTMLResponse)
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants incorrects"})

    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False,
        path="/"
    )
    return response

from fastapi import Depends, HTTPException, status
from functools import wraps
from typing import Callable
from app.routers.auth import get_current_user
from app import models

def require_roles(*allowed_roles: str):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, current_user: models.Utilisateur = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="⛔ Accès refusé. Rôle non autorisé."
                )
            return func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 🔓 Déconnexion (supprime le cookie)
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return RedirectResponse(url="/login", status_code=303)
