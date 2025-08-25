#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请求策略基类
定义了所有请求策略必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseRequestStrategy(ABC):
    """请求策略基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化策略
        
        Args:
            config: 策略配置
        """
        self.config = config or {}
    
    @abstractmethod
    async def init(self):
        """初始化策略"""
        pass
    
    @abstractmethod
    async def get(self, url: str, headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送 GET 请求
        
        Args:
            url: 请求URL
            headers: 请求头
            **kwargs: 其他请求选项
            
        Returns:
            响应数据字典
        """
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Any = None, headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送 POST 请求
        
        Args:
            url: 请求URL
            data: 请求数据
            headers: 请求头
            **kwargs: 其他请求选项
            
        Returns:
            响应数据字典
        """
        pass
    
    @abstractmethod
    async def destroy(self):
        """清理资源"""
        pass
    
    def get_name(self) -> str:
        """
        获取策略名称
        
        Returns:
            策略名称
        """
        return self.__class__.__name__