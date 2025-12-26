from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def get_global_stats(db: Session):
    total_familles = db.query(models.Famille).count()
    total_membres = db.query(models.Membre).count()

    stats_par_localisation = (
        db.query(models.Famille.localisation, func.count(models.Famille.id))
        .group_by(models.Famille.localisation)
        .all()
    )

    return {
        "total_familles": total_familles,
        "total_membres": total_membres,
        "par_localisation": stats_par_localisation
    }

def get_stats_par_agent(db: Session):
    stats_agents = (
        db.query(models.Utilisateur.username, func.count(models.Famille.id))
        .join(models.Famille, models.Utilisateur.id == models.Famille.created_by_id)
        .group_by(models.Utilisateur.username)
        .all()
    )

    return [{"agent": agent, "familles_renseignees": count} for agent, count in stats_agents]
