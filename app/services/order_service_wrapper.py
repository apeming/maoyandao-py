#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
订单服务包装器 - 为 FastAPI 提供异步接口
"""

import logging
import hashlib
from typing import Dict, Any

from app.core.order_service import OrderService
from app.models.order import OrderRequest, OrderResponse, OrderType
from app.core.config import settings


logger = logging.getLogger(__name__)


class OrderServiceWrapper:
    """订单服务包装器类"""
    
    def __init__(self):
        self._service_cache: Dict[str, OrderService] = {}
    
    async def create_service(self, private_key: str):
        await self._get_or_create_service(private_key)

    async def _get_or_create_service(self, private_key) -> OrderService:
        """
        获取或创建订单服务实例（带缓存）
        
        Args:
            private_key: 私钥
            options: 配置选项
        
        Returns:
            订单服务实例
        """
        # 使用私钥的哈希作为缓存键（安全考虑）
        cache_key = hashlib.sha256(private_key.encode()).hexdigest()[:16]
        
        if cache_key not in self._service_cache:
            # 合并默认配置和用户配置
            default_options = {
                'rpc_url': settings.rpc_url,
                'timeout': settings.request_timeout,
                'use_proxy': settings.use_proxy,
                'proxy_file': settings.proxy_file,
            }
            
            # 创建新的服务实例
            service = OrderService(private_key, default_options)
            await service.init()
            await service.login()
            
            # 缓存服务实例
            self._service_cache[cache_key] = service
        
        return self._service_cache[cache_key]

    async def login(self, private_key: str):
        try:
            service = await self._get_or_create_service(private_key)
            await service.login()
        except:
            pass

    async def get_markets(self, filter, private_key):
        try:
            service = await self._get_or_create_service(private_key)
            markets = await service.get_markets(filter)
            return markets
        except:
            return []

    async def place_order(self, request: OrderRequest, private_key: str) -> OrderResponse:
        """
        下单接口
        
        Args:
            request: 订单请求
            private_key: 私钥（从配置中获取）
            
        Returns:
            订单响应
        """
        try:
            # 获取订单服务实例
            service = await self._get_or_create_service(private_key)
            
            # 准备订单参数
            order_params = {
                'nft_token_id': request.nft_token_id,
            }
            
            # 执行登录（如果需要）
            if not service.is_authenticated():
                await service.login()
            
            # 根据订单类型下单
            if request.order_type == OrderType.MARKET:
                # 市价单：获取当前价格作为 token_amount
                current_price = request.price_wei
                created_at_ts = request.created_at_ts

                if not current_price or not created_at_ts:
                    item_details = await service.get_item_details(request.nft_token_id)
                    sales_info = item_details['salesInfo']
                    current_price = sales_info['priceWei']
                    created_at_ts = item_details['createdAtTs']

                if not current_price:
                    return OrderResponse(
                        success=False,
                        message="商品当前不在售，无法下市价单",
                        error_code="ITEM_NOT_FOR_SALE"
                    )
                
                # 使用当前价格作为 token_amount
                order_params['token_amount'] = current_price
                order_params['created_at_ts'] = int(created_at_ts)
                
                # 下市价单
                response = await service.place_market_order(
                    order_params, 
                    confirm_real_order=request.confirm_real_order
                )
            
            elif request.order_type == OrderType.LIMIT:
                # 限价单：使用用户提供的 amount
                if not request.amount:
                    return OrderResponse(
                        success=False,
                        message="限价单必须提供 amount 参数",
                        error_code="MISSING_AMOUNT"
                    )
                
                order_params['amount'] = request.amount
                
                # 下限价单
                response = await service.place_limit_order(
                    order_params, 
                    confirm_real_order=request.confirm_real_order
                )
            
            elif request.order_type == OrderType.SELL:
                if not request.token_amount:
                    return OrderResponse(
                        success=False,
                        message="卖单必须提供 token_amount 参数",
                        error_code="MISSING_TOKEN_AMOUNT"
                    )

                order_params['token_amount'] = request.price_wei
                
                response = await service.place_sell_order(
                    order_params,
                    confirm_real_order=request.confirm_real_order
                )

            else:
                return OrderResponse(
                    success=False,
                    message=f"不支持的订单类型: {request.order_type}",
                    error_code="UNSUPPORTED_ORDER_TYPE"
                )
            
            # 处理响应
            if response.get('success', False):
                return OrderResponse(
                    success=True,
                    message="订单创建成功",
                    order_data=response.get('data'),
                    transaction_hash=response.get('data', {}).get('transactionHash')
                )
            else:
                return OrderResponse(
                    success=False,
                    message=f"订单创建失败: {response.get('error', '未知错误')}",
                    error_code="ORDER_CREATION_FAILED",
                    order_data=response.get('data')
                )
        
        except ValueError as e:
            # 参数验证错误
            return OrderResponse(
                success=False,
                message=f"参数错误: {str(e)}",
                error_code="INVALID_PARAMETERS"
            )
        
        except Exception as e:
            # 其他错误
            error_message = str(e)
            error_code = "UNKNOWN_ERROR"
            
            # 识别常见错误类型
            if "安全检查" in error_message:
                error_code = "SECURITY_CHECK_FAILED"
            elif "未认证" in error_message:
                error_code = "AUTHENTICATION_REQUIRED"
            elif "请求太频繁" in error_message:
                error_code = "RATE_LIMITED"
            elif "请求被封禁" in error_message:
                error_code = "REQUEST_BLOCKED"

            logger.error(f'下单失败: error_code: {error_code}, error_message: {error_message}')
            
            return OrderResponse(
                success=False,
                message=error_message,
                error_code=error_code
            )
    
    async def cleanup(self):
        """清理所有缓存的服务实例"""
        for service in self._service_cache.values():
            try:
                await service.destroy()
            except Exception as e:
                print(f"清理服务实例时出错: {e}")
        
        self._service_cache.clear()


# 全局服务实例
order_service_wrapper = OrderServiceWrapper()