from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_class=PlainTextResponse)
async def get_metrics():
    # TODO: Implement Prometheus metrics
    return "# HELP veaf_app_info Application info\n# TYPE veaf_app_info gauge\nveaf_app_info{version=\"2.0.0\"} 1\n"
