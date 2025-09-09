"""任务定义模块"""
import asyncio
import logging
from typing import Dict, Any

from app.core.config import settings
from app.models.order import OrderRequest, OrderResponse, ErrorResponse, OrderType
from app.services.order_service_wrapper import order_service_wrapper

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

    @staticmethod
    async def _fetch_market(filter):
        try:
            markets = await order_service_wrapper.get_markets(filter)
            other_markets = [
                market for market in markets
                if filter['categoryNo'] != 0
                and market['category_no'] != filter['categoryNo']
            ]

            if (len(other_markets) != 0 or len(markets) > 50):
                logger.warning('获取错误')
                return

            logger.info(f"发现{len(markets)}个{filter['categoryNo']}新市场")
            for market in markets:
                nft_token_id = market['token_id']
                price_wei = market['price_wei']
                created_at_ts = market['created_at_ts']

                logger.info(f'{nft_token_id:}, {price_wei:}, {created_at_ts:}')

                # request = OrderRequest(
                #     nft_token_id=nft_token_id,
                #     order_type='market',
                #     price_wei=price_wei,
                #     created_at_ts=created_at_ts,
                #     confirm_real_order=True,
                #     use_proxy=True,
                #     timeout=settings.request_timeout,
                # )

                # order_service_wrapper.place_order(
                #     request=request,
                #     private_key=settings.private_key
                # )
        except Exception as e:
            pass

    @staticmethod
    async def get_new_markets():
        try:
            logger.info("开始监听新市场...")
            filters = [
                {
                    "categoryNo": 1000401001,
                    "petSkills": [5190016],
                    "price": {"min":0,"max":20000000}
                },
                {
                    "categoryNo": 1000401001,
                    "petSkills": [5190010],
                    "price": {"min": 0,"max": 1000000}
                },
                {
                    "categoryNo": 0,
                    "price": {"min": 0, "max": 3000},
                    "level": {"min": 0, "max": 250},
                    "starforce": {"min": 0, "max": 25},
                    "potential": {"min": 0, "max": 4},
                    "bonusPotential": {"min": 0, "max": 4}
                },
            ]
            await asyncio.gather(*(TaskRegistry._fetch_market(f) for f in filters))

        except:
            logger.error("新市场发现失败...")

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
            "get_new_markets": {
                "func": cls.get_new_markets,
                "type": "interval",
                "seconds": 10,
                "start_immediately": True,
                "description": "发现新市场任务"
            }
        }
