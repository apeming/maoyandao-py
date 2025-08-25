#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理管理器
负责从代理文件中随机选择代理
"""

import random
import os
from typing import Optional, List


class ProxyManager:
    """代理管理器类"""
    
    def __init__(self, proxy_file: str = 'proxies.txt'):
        """
        初始化代理管理器
        
        Args:
            proxy_file: 代理文件路径
        """
        self.proxy_file = proxy_file
        self._proxies = []
        self._last_modified = 0
    
    def _load_proxies(self) -> List[str]:
        """
        从文件加载代理列表
        
        Returns:
            代理列表
        """
        if not os.path.exists(self.proxy_file):
            print(f'代理文件 {self.proxy_file} 不存在')
            return []
        
        try:
            # 检查文件修改时间
            current_modified = os.path.getmtime(self.proxy_file)
            if current_modified != self._last_modified:
                with open(self.proxy_file, 'r', encoding='utf-8') as f:
                    proxies = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 确保代理格式正确
                            if not line.startswith('http://') and not line.startswith('https://'):
                                line = 'http://' + line
                            proxies.append(line)
                    
                    self._proxies = proxies
                    self._last_modified = current_modified
                    print(f'已加载 {len(self._proxies)} 个代理')
            
            return self._proxies
        except Exception as e:
            print(f'加载代理文件失败: {e}')
            return []
    
    def get_random_proxy(self) -> Optional[str]:
        """
        获取随机代理
        
        Returns:
            随机选择的代理URL，如果没有可用代理则返回None
        """
        proxies = self._load_proxies()
        if not proxies:
            return None
        
        return random.choice(proxies)
    
    def get_proxy_count(self) -> int:
        """
        获取可用代理数量
        
        Returns:
            代理数量
        """
        proxies = self._load_proxies()
        return len(proxies)
    
    def is_available(self) -> bool:
        """
        检查是否有可用代理
        
        Returns:
            是否有可用代理
        """
        return self.get_proxy_count() > 0