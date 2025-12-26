from fastapi import APIRouter, HTTPException, Depends, Path, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import database, models
import csv
import io
import json

router = APIRouter(tags=["attribution"])


class AttributionZone(BaseModel):
    utilisateur_id: int
    geojson: dict  # ou str si tu préfères stocker le GeoJSON en texte


@router.post("/api/attribuer-zone", response_class=JSONResponse)
def attribuer_zone(data: AttributionZone, db: Session = Depends(database.get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.id == data.utilisateur_id).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    zone = models.Zone(
        utilisateur_id=data.utilisateur_id,
        geometrie=data.geojson
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)

    return {"message": "Zone attribuée avec succès", "zone_id": zone.id}


@router.put("/api/zones/{zone_id}", response_class=JSONResponse)
def mettre_a_jour_zone(
    zone_id: int = Path(...),
    data: AttributionZone = Depends(),
    db: Session = Depends(database.get_db)
):
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")

    zone.geometrie = data.geojson
    db.commit()
    return {"message": "Zone mise à jour avec succès"}


@router.post("/api/importer-zones", response_class=JSONResponse)
def importer_zones(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    count = 0

    for row in reader:
        try:
            utilisateur_id = int(row["utilisateur_id"])
            geojson = json.loads(row["geojson"])

            zone = models.Zone(utilisateur_id=utilisateur_id, geometrie=geojson)
            db.add(zone)
            count += 1
        except Exception:
            continue  # Ignore les lignes invalides

    db.commit()
    return {"message": f"{count} zones importées avec succès"}
