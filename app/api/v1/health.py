#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查 API 路由
"""

from datetime import datetime

from fastapi import APIRouter

from app.models.order import HealthResponse
from app.core.config import settings


router = APIRouter(prefix="/api/v1", tags=["健康检查"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务运行状态"
)
async def health_check():
    """健康检查接口"""
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now().isoformat()
    )