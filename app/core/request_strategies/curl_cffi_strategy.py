#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
curl_cffi 请求策略
使用 curl_cffi 库进行 HTTP 请求，适合绕过基本的反爬虫检测
"""

from typing import Dict, Any, Optional
from curl_cffi import requests
from .base_request_strategy import BaseRequestStrategy
from .proxy_manager import ProxyManager


class CurlCffiStrategy(BaseRequestStrategy):
    """curl_cffi 请求策略"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        self.session = None
        self.cookies = {}  # 存储 cookies，包括 wat 和 wrt
        
        # 代理管理器
        self.proxy_manager = ProxyManager(config.get('proxy_file', 'proxies.txt'))
        
        # 默认配置
        self.default_options = {
            'timeout': config.get('timeout', 15),
            'impersonate': config.get('impersonate', 'chrome120'),
            'use_proxy': config.get('use_proxy', True)
        }
    
    async def init(self):
        """初始化策略"""
        if not self.session:
            # 创建异步会话
            self.session = requests.AsyncSession(
                impersonate=self.default_options['impersonate'],
                timeout=self.default_options['timeout']
            )

            # 设置默认头部
            self.session.headers.update({
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            })
    
    def _get_proxy_config(self) -> Optional[str]:
        """
        获取代理配置
        
        Returns:
            代理URL或None
        """
        if not self.default_options['use_proxy']:
            return None
        
        proxy = self.proxy_manager.get_random_proxy()

        return proxy
    
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
        await self.init()
        
        # 合并请求头
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # 设置 cookies
        cookies_to_send = {**self.cookies}
        
        # 获取代理配置
        proxy = self._get_proxy_config()
        if proxy:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}
        
        try:
            response = await self.session.get(
                url,
                headers=request_headers,
                cookies=cookies_to_send,
                **kwargs
            )
            
            return self._format_response(response)
            
        except Exception as error:
            raise error
    
    async def post(self, url: str, payload: Any = None, headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
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
        await self.init()
        
        # 合并请求头
        request_headers = {
            'Content-Type': 'application/json'
        }
        if headers:
            request_headers.update(headers)
        

        # 设置 cookies
        cookies_to_send = {**self.cookies}
        
        # 获取代理配置
        proxy = self._get_proxy_config()
        if proxy:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}

        try:
            response = await self.session.post(
                url,
                json=payload,
                headers=request_headers,
                cookies=cookies_to_send,
                **kwargs
            )
            
            return self._format_response(response)
            
        except Exception as error:
            raise error
    

    def _format_response(self, response) -> Dict[str, Any]:
        """
        格式化响应数据，统一响应格式
        
        Args:
            response: HTTP 响应对象
            
        Returns:
            格式化的响应数据字典
        """
        try:
            # 尝试解析 JSON 响应
            response_data = response.json()
        except:
            # 如果不是 JSON，返回文本内容
            response_data = response.text
        
        return {
            'status': response.status_code,
            'status_text': response.reason or '',
            'headers': dict(response.headers),
            'data': response_data,
            'success': 200 <= response.status_code < 300
        }
    
    def set_cookies(self, cookies: Dict[str, str]):
        """
        手动设置 cookies
        
        Args:
            cookies: 要设置的 cookies
        """
        self.cookies.update(cookies)
    
    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前存储的 cookies
        
        Returns:
            当前存储的 cookies
        """
        return self.cookies.copy()
    
    def clear_cookies(self):
        """清除所有 cookies"""
        self.cookies.clear()
    
    def get_proxy_info(self) -> Dict[str, Any]:
        """
        获取代理信息
        
        Returns:
            代理信息字典
        """
        return {
            'use_proxy': self.default_options['use_proxy'],
            'proxy_count': self.proxy_manager.get_proxy_count(),
            'proxy_available': self.proxy_manager.is_available()
        }
    
    def set_proxy_enabled(self, enabled: bool):
        """
        启用或禁用代理
        
        Args:
            enabled: 是否启用代理
        """
        self.default_options['use_proxy'] = enabled
    
    async def destroy(self):
        """清理资源"""
        if self.session:
            await self.session.close()
            self.session = None