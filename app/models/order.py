#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
订单相关数据模型
"""

from typing import Optional, Union
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class OrderType(str, Enum):
    """订单类型枚举"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"    # 限价单


class OrderRequest(BaseModel):
    """订单请求模型（GET 请求参数）"""
    
    # 必需字段
    nft_token_id: str = Field(..., description="NFT 代币ID")
    
    # 可选字段
    order_type: OrderType = Field(OrderType.MARKET, description="订单类型：market（市价单）或 limit（限价单），默认为 market")
    amount: Optional[Union[str, int, float]] = Field(None, description="代币数量（限价单时必需，会自动转换为 wei 单位）")
    price_wei: Optional[str] = Field(None, description="价格，单位wei")
    created_at_ts: Optional[int] = Field(None, description="商品上架时间戳")
    confirm_real_order: bool = Field(False, description="确认下真实订单的安全检查参数")
    
    # 可选配置
    rpc_url: Optional[str] = Field(None, description="RPC URL")
    use_proxy: Optional[bool] = Field(None, description="是否使用代理")
    timeout: Optional[int] = Field(None, description="请求超时时间（秒）")
    
    @model_validator(mode='after')
    def validate_amount_for_limit_order(self) -> 'OrderRequest':
        """验证限价单的数量字段"""
        # 如果是限价单，必须提供 amount
        if self.order_type == OrderType.LIMIT and not self.amount:
            raise ValueError('限价单必须提供 amount 参数')
        
        return self
    
    @model_validator(mode='after')
    def validate_confirmation(self) -> 'OrderRequest':
        """验证安全确认"""
        if not self.confirm_real_order:
            raise ValueError('安全检查：您必须设置 confirm_real_order=True 来下真实订单')
        return self


class OrderResponse(BaseModel):
    """订单响应模型"""
    
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    order_id: Optional[str] = Field(None, description="订单ID")
    transaction_hash: Optional[str] = Field(None, description="交易哈希")
    order_data: Optional[dict] = Field(None, description="订单详细数据")
    error_code: Optional[str] = Field(None, description="错误代码")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[dict] = Field(None, description="错误详情")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="应用版本")
    timestamp: str = Field(..., description="检查时间")