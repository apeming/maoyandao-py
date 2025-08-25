#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请求策略工厂
负责创建和管理不同的请求策略实例
"""

from typing import Dict, Any, List
from .base_request_strategy import BaseRequestStrategy
from .curl_cffi_strategy import CurlCffiStrategy


class RequestStrategyFactory:
    """请求策略工厂类"""
    
    STRATEGIES = {
        'CURL_CFFI': 'curl_cffi'
    }
    
    @classmethod
    def create(cls, strategy_type: str, config: Dict[str, Any] = None) -> BaseRequestStrategy:
        """
        创建请求策略实例
        
        Args:
            strategy_type: 策略类型
            config: 策略配置
            
        Returns:
            策略实例
            
        Raises:
            ValueError: 不支持的策略类型
        """
        if config is None:
            config = {}
            
        strategy_type_lower = strategy_type.lower()
        
        if strategy_type_lower == cls.STRATEGIES['CURL_CFFI']:
            return CurlCffiStrategy(config)
        else:
            raise ValueError(f"不支持的请求策略类型: {strategy_type}")
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """
        获取所有可用的策略类型
        
        Returns:
            策略类型列表
        """
        return list(cls.STRATEGIES.values())
    
    @classmethod
    def is_valid_strategy(cls, strategy_type: str) -> bool:
        """
        检查策略类型是否有效
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            是否有效
        """
        return strategy_type.lower() in cls.STRATEGIES.values()