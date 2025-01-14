import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymilvus import connections, utility

from app.common_copy.config import llm_config, service_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def read_root():
    return {"config": llm_config["model_name"]}


@router.get("/health")
async def health():
    status = {
        "status": "unhealthy" if any(v["error"] is not None for v in service_status.values()) else "healthy",
        "details": service_status
    }

    return status


@router.get("/metrics")
async def metrics():
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
