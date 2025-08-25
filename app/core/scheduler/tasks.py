"""任务定义模块"""
import logging
from typing import Dict, Any
from app.services.order_service_wrapper import order_service_wrapper
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaskRegistry:
    """任务注册表"""
    
    @staticmethod
    async def periodic_login_task():
        """定时登录任务"""
        try:
            logger.info("🔐 开始执行定时登录...")
            await order_service_wrapper.login(settings.private_key)
            logger.info("✅ 定时登录完成")
        except Exception as e:
            logger.error(f"❌ 定时登录失败: {e}")
            raise e

    @classmethod
    def get_task_config(cls) -> Dict[str, Dict[str, Any]]:
        """获取任务配置"""
        return {
            "periodic_login": {
                "func": cls.periodic_login_task,
                "type": "interval",
                "seconds": 600,  # 10分钟
                "start_immediately": False,
                "description": "定时登录任务"
            },
        }
