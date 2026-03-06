from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.version import APP_VERSION

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_class=PlainTextResponse)
async def get_metrics():
    # TODO: Implement Prometheus metrics
    return f'# HELP veaf_app_info Application info\n# TYPE veaf_app_info gauge\nveaf_app_info{{version="{APP_VERSION}"}} 1\n'
