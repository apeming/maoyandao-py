#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用配置模块
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    app_name: str = "订单服务 API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 区块链配置
    rpc_url: str = "https://mainnet.base.org"
    private_key: Optional[str] = None  # 从环境变量获取私钥
    
    # 请求策略配置
    request_timeout: int = 3
    use_proxy: bool = True
    proxy_file: str = "proxies.txt"
    concurrent_interval_ms: int = 5
    
    # 安全配置
    require_confirmation: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # 忽略额外的环境变量
    }


# 全局配置实例
settings = Settings()