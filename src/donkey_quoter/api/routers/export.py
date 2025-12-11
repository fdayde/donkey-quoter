"""
Router pour les endpoints /export.
"""

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..auth import OptionalAPIKey
from ..dependencies import QuoteRepo, Storage
from ..schemas import ExportResponse

router = APIRouter(prefix="/export", tags=["export"])


@router.get(
    "",
    response_model=ExportResponse,
    summary="Exporter toutes les données",
)
async def export_all(
    repo: QuoteRepo,
    storage: Storage,
    api_key: OptionalAPIKey = None,
):
    """Exporte toutes les citations et haïkus."""
    return ExportResponse(
        quotes=repo.quotes,
        haikus=storage.haikus_data,
        export_date=datetime.utcnow(),
        total_quotes=len(repo.quotes),
    )


@router.get(
    "/download",
    summary="Télécharger l'export en fichier JSON",
)
async def download_export(
    repo: QuoteRepo,
    storage: Storage,
    api_key: OptionalAPIKey = None,
):
    """Télécharge toutes les données sous forme de fichier JSON."""
    data = {
        "quotes": [q.model_dump() for q in repo.quotes],
        "haikus": storage.haikus_data,
        "export_date": datetime.utcnow().isoformat(),
        "total_quotes": len(repo.quotes),
    }

    filename = f"donkey-quoter-export-{datetime.now().strftime('%Y%m%d')}.json"

    return JSONResponse(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
