#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
订单 API 路由
"""

from typing import Optional, Union
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.models.order import OrderRequest, OrderResponse, ErrorResponse, OrderType
from app.services.order_service_wrapper import order_service_wrapper


router = APIRouter(prefix="/api/v1", tags=["订单"])


@router.get(
    "/order",
    response_model=OrderResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
    summary="创建订单",
    description="""
    创建市价单或限价单。
    
    **订单类型说明：**
    - `market`: 市价单 - 以当前市场价格立即执行（默认）
    - `limit`: 限价单 - 以指定价格挂单等待成交
    
    **参数说明：**
    - `nft_token_id`: NFT 代币ID（必需）
    - `order_type`: 订单类型，默认为 market
    - `amount`: 代币数量（限价单时必需，会自动转换为 wei 单位）
    - `confirm_real_order`: 安全确认参数，必须为 true
    
    **私钥获取：**
    - 私钥从环境变量 PRIVATE_KEY 中自动获取
    
    **安全要求：**
    - 必须设置 `confirm_real_order=true` 才能下真实订单
    - 这是为了防止测试过程中的意外下单
    """
)
async def create_order(
    nft_token_id: str,
    order_type: OrderType = OrderType.MARKET,
    amount: Optional[Union[str, int, float]] = None,
    price_wei: Optional[str] = None,
    created_at_ts: Optional[int] = None,
    confirm_real_order: bool = False,
    rpc_url: Optional[str] = None,
    use_proxy: Optional[bool] = None,
    timeout: Optional[int] = None
):
    """创建订单接口"""
    
    try:
        if not settings.private_key:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    message="服务器配置错误：未设置 PRIVATE_KEY 环境变量",
                    error_code="MISSING_PRIVATE_KEY"
                ).model_dump()
            )
        
        # 构建请求对象
        request = OrderRequest(
            nft_token_id=nft_token_id,
            order_type=order_type,
            amount=amount,
            price_wei=price_wei,
            created_at_ts=created_at_ts,
            confirm_real_order=confirm_real_order or (not settings.require_confirmation),
            rpc_url=rpc_url,
            use_proxy=use_proxy,
            timeout=timeout
        )
        
        # 调用订单服务
        result = await order_service_wrapper.place_order(request, settings.private_key)
        
        # 根据结果返回相应的状态码
        if result.success:
            return result
        else:
            # 根据错误类型返回不同的状态码
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            if result.error_code in ["INVALID_PARAMETERS", "SECURITY_CHECK_FAILED"]:
                status_code = status.HTTP_400_BAD_REQUEST
            elif result.error_code == "AUTHENTICATION_REQUIRED":
                status_code = status.HTTP_401_UNAUTHORIZED
            elif result.error_code == "RATE_LIMITED":
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif result.error_code == "REQUEST_BLOCKED":
                status_code = status.HTTP_403_FORBIDDEN
            
            return JSONResponse(
                status_code=status_code,
                content=result.model_dump()
            )
    
    except Exception as e:
        # 未预期的错误
        error_response = ErrorResponse(
            message=f"服务器内部错误: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


@router.get(
    "/sell",
    response_model=OrderResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
    summary="创建卖单",
    description="""
    创建卖单。
    
    **参数说明：**
    - `nft_token_id`: NFT 代币ID（必需）
    - `token_amount`: 代币数量（wei 单位）
    - `confirm_real_order`: 安全确认参数，必须为 true
    
    **私钥获取：**
    - 私钥从环境变量 PRIVATE_KEY 中自动获取
    
    **安全要求：**
    - 必须设置 `confirm_real_order=true` 才能下真实订单
    - 这是为了防止测试过程中的意外下单
    """
)
async def create_sell_order(
    nft_token_id: str,
    price_wei: str,
    confirm_real_order: bool = False,
    rpc_url: Optional[str] = None,
    use_proxy: Optional[bool] = None,
    timeout: Optional[int] = None
):
    """创建卖单接口"""
    
    try:
        if not settings.private_key:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    message="服务器配置错误：未设置 PRIVATE_KEY 环境变量",
                    error_code="MISSING_PRIVATE_KEY"
                ).model_dump()
            )
        
        # 构建请求对象
        request = OrderRequest(
            nft_token_id=nft_token_id,
            order_type=OrderType.SELL,
            price_wei=price_wei,
            confirm_real_order=confirm_real_order or (not settings.require_confirmation),
            rpc_url=rpc_url,
            use_proxy=use_proxy,
            timeout=timeout
        )
        
        # 调用订单服务
        result = await order_service_wrapper.place_order(request, settings.private_key)
        
        # 根据结果返回相应的状态码
        if result.success:
            return result
        else:
            # 根据错误类型返回不同的状态码
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            if result.error_code in ["INVALID_PARAMETERS", "SECURITY_CHECK_FAILED"]:
                status_code = status.HTTP_400_BAD_REQUEST
            elif result.error_code == "AUTHENTICATION_REQUIRED":
                status_code = status.HTTP_401_UNAUTHORIZED
            elif result.error_code == "RATE_LIMITED":
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif result.error_code == "REQUEST_BLOCKED":
                status_code = status.HTTP_403_FORBIDDEN
            
            return JSONResponse(
                status_code=status_code,
                content=result.model_dump()
            )
    
    except Exception as e:
        # 未预期的错误
        error_response = ErrorResponse(
            message=f"服务器内部错误: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
