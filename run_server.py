#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 服务器启动脚本
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"🌟 启动 {settings.app_name} v{settings.app_version}")
    print(f"📡 服务地址: http://{settings.host}:{settings.port}")
    print(f"📚 API 文档: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 调试模式: {'开启' if settings.debug else '关闭'}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )