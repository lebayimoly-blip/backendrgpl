
from fastapi import Depends
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
import os
from app.config import settings


from app.database import Base, engine, SessionLocal
from app.routers import familles, utilisateurs, statistiques, pages, auth, admin, doublons, zones
from app import models, schemas, crud
from app.routers import attribution
from fastapi.middleware.cors import CORSMiddleware

# 📦 Initialisation de l'application
app = FastAPI()

origins = [
    "https://glittering-halva-334c3f.netlify.app",
    "http://localhost:3000",  # utile pour tests locaux
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.mount("/static", StaticFiles(directory="static"), name="static")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# 🔗 Inclusion des routeurs
# 🔗 Inclusion des routeurs avec préfixe /api
app.include_router(auth.router, prefix="/api")
app.include_router(familles.router, prefix="/api")
app.include_router(utilisateurs.router, prefix="/api")
app.include_router(statistiques.router, prefix="/api")
app.include_router(doublons.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(attribution.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(pages.router, prefix="/api")
app.include_router(offline.router, prefix="/api")

# 🗃️ Création des tables de la base de données
Base.metadata.create_all(bind=engine)

# 👤 Création automatique du super utilisateur
def init_super_user():
    db = SessionLocal()
    if not db.query(models.Utilisateur).filter_by(username="lebayi moly").first():
        crud.create_utilisateur(db, schemas.UtilisateurCreate(
            username="lebayi moly",
            password="Google99.",
            role="super_utilisateur"
        ))
        print("✅ Super utilisateur 'lebayi moly' créé.")
    else:
        print("ℹ️ Super utilisateur déjà existant.")
    db.close()

init_super_user()

@app.get("/test-auth")
def test_auth(current_user: models.Utilisateur = Depends(auth.get_current_user)):
    return {"message": f"Bienvenue {current_user.username} !"}

@app.get("/synchronisation", response_class=HTMLResponse)
async def synchronisation(request: Request):
    return templates.TemplateResponse("synchronisation.html", {"request": request})

@app.get("/offline.html", response_class=HTMLResponse)
async def offline(request: Request):
    return templates.TemplateResponse("offline.html", {"request": request})

from app.routers import offline
app.include_router(offline.router)

from fastapi.responses import FileResponse

@app.get("/service-worker.js")
async def service_worker():
    return FileResponse("static/service-worker.js", media_type="application/javascript")

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    users = db.query(models.Utilisateur).all()
    return {"utilisateurs": [u.username for u in users]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
