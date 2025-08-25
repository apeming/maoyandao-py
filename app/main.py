#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 应用主入口
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.scheduler import SchedulerManager, TaskRegistry
from app.api.v1 import order, health
from app.services.order_service_wrapper import order_service_wrapper


# 统一配置日志 - 在所有其他导入之前
logger = setup_logging(
    level="INFO",
    apscheduler_level="INFO"  # 设置为 INFO 可以看到定时任务执行日志
    # apscheduler_level="WARNING"  # 设置为 WARNING 可以减少日志噪音
)

# 全局调度器管理器
scheduler_manager = SchedulerManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    print(f"🚀 {settings.app_name} v{settings.app_version} 正在启动...")
    await order_service_wrapper.create_service(settings.private_key)
    # 启动调度器
    await scheduler_manager.start()

    # 注册任务
    await _register_scheduled_tasks()

    yield
    
    # 关闭时的清理
    print("🔄 正在清理资源...")
    try:
        # 优雅关闭调度器
        await scheduler_manager.shutdown(wait=True, timeout=30.0)
        # 清理其他资源
        await order_service_wrapper.cleanup()
        logger.info("✅ 资源清理完成")
    except Exception as e:
        logger.error(f"❌ 清理资源时出错: {e}")

async def _register_scheduled_tasks():
    """注册定时任务"""
    task_config = TaskRegistry.get_task_config()
    
    for job_id, config in task_config.items():
        try:
            if config["type"] == "interval":
                scheduler_manager.add_interval_job(
                    func=config["func"],
                    seconds=config["seconds"],
                    job_id=job_id,
                    start_immediately=config.get("start_immediately", False)
                )
            elif config["type"] == "cron":
                scheduler_manager.add_cron_job(
                    func=config["func"],
                    cron_expression=config["cron_expression"],
                    job_id=job_id
                )
            
            logger.info(f"✅ 任务已注册: {job_id} - {config['description']}")
            
        except Exception as e:
            logger.error(f"❌ 注册任务失败 {job_id}: {e}")

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## 订单服务 API
    
    提供市价单和限价单的创建功能，支持 NFT 交易。
    
    ### 主要功能
    - 🛒 创建市价单（以当前市场价格立即执行）
    - 📋 创建限价单（以指定价格挂单等待成交）
    - 💰 获取商品当前价格
    - 🔍 健康检查
    
    ### 安全特性
    - ✅ 强制确认机制防止意外下单
    - 🔐 私钥安全处理
    - 🚦 请求频率限制
    - 🛡️ 代理支持
    
    ### 使用说明
    1. 所有真实订单都需要设置 `confirm_real_order=true`
    2. 支持两种数量格式：用户友好的 `amount` 或精确的 `token_amount`
    3. 市价单会自动获取当前价格，限价单使用指定价格
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(order.router)
app.include_router(health.router)


@app.get("/", tags=["根路径"])
async def root():
    """根路径接口"""
    return {
        "message": f"欢迎使用 {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"🌟 启动 {settings.app_name} v{settings.app_version}")
    print(f"📡 服务地址: http://{settings.host}:{settings.port}")
    print(f"📚 API 文档: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )