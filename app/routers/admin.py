from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, database
from app.routers import auth

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Middleware : accès réservé aux super utilisateurs
def require_super_user(current_user: models.Utilisateur = Depends(auth.get_current_user)):
    if current_user.role != "super_utilisateur":
        raise HTTPException(status_code=403, detail="Accès réservé aux super utilisateurs")
    return current_user

# Tableau de bord admin
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.Utilisateur = Depends(require_super_user)
):
    total_users = db.query(models.Utilisateur).count()
    total_familles = db.query(models.Famille).count()
    total_membres = db.query(models.Membre).count()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": current_user,
        "total_users": total_users,
        "total_familles": total_familles,
        "total_membres": total_membres
    })
