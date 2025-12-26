import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config import settings
from app.database import Base, engine, SessionLocal, get_db
from app.routers import familles, utilisateurs, statistiques, pages, auth, admin, doublons, zones, attribution, offline
from app import models, schemas, crud

# 📦 Initialisation de l'application
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# 🔐 Gestionnaire d'erreurs HTTP
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_401_UNAUTHORIZED:
        return templates.TemplateResponse(
            "unauthorized.html",
            {"request": request, "detail": exc.detail},
            status_code=401
        )
    return PlainTextResponse(f"Erreur {exc.status_code} : {exc.detail}", status_code=exc.status_code)

# 📁 Fichiers statiques
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# 🔗 Inclusion des routeurs
app.include_router(familles.router)
app.include_router(utilisateurs.router)
app.include_router(statistiques.router)
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doublons.router)
app.include_router(zones.router)
app.include_router(attribution.router)
app.include_router(offline.router)

# 🗃️ Création des tables de la base de données
Base.metadata.create_all(bind=engine)

# 👤 Création automatique du super utilisateur
def init_super_user():
    db = SessionLocal()
    if not db.query(models.Utilisateur).filter_by(username="lebayi moly").first():
        crud.create_utilisateur(db, schemas.UtilisateurCreate(
            username="lebayi moly",
            password="Google99.",  # ⚠️ à remplacer par un mot de passe hashé
            role="super_utilisateur"
        ))
        print("✅ Super utilisateur 'lebayi moly' créé.")
    else:
        print("ℹ️ Super utilisateur déjà existant.")
    db.close()

init_super_user()

# 🔧 Routes utilitaires
@app.get("/test-auth")
def test_auth(current_user: models.Utilisateur = Depends(auth.get_current_user)):
    return {"message": f"Bienvenue {current_user.username} !"}

@app.get("/synchronisation", response_class=HTMLResponse)
async def synchronisation(request: Request):
    return templates.TemplateResponse("synchronisation.html", {"request": request})

@app.get("/offline.html", response_class=HTMLResponse)
async def offline_page(request: Request):
    return templates.TemplateResponse("offline.html", {"request": request})

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    users = db.query(models.Utilisateur).all()
    return {"utilisateurs": [u.username for u in users]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
