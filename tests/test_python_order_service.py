#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python 原生订单服务测试
测试 OrderService 类的各项功能
"""

import pytest
import pytest_asyncio
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.order_service import OrderService


class TestOrderService:
    """订单服务测试类"""
    
    @pytest.fixture
    def test_private_key(self):
        """测试私钥"""
        return "0x" + "1" * 64
    
    @pytest_asyncio.fixture
    async def order_service(self, test_private_key):
        """创建订单服务实例"""
        service = OrderService(test_private_key)
        await service.init()
        yield service
        await service.destroy()
    
    def test_timestamp_functionality(self, order_service):
        """测试时间戳功能"""
        # 测试当前时间戳
        timestamp_info = order_service.get_timestamp(0)
        assert 'ms' in timestamp_info
        assert 'sec' in timestamp_info
        assert 'after_days_sec' in timestamp_info
        assert timestamp_info['after_days_sec'] == timestamp_info['sec']
        
        # 测试 7 天后
        timestamp_info_7d = order_service.get_timestamp(7)
        expected_diff = 7 * 86400  # 7天的秒数
        actual_diff = timestamp_info_7d['after_days_sec'] - timestamp_info_7d['sec']
        assert actual_diff == expected_diff
        
        # 测试负数（过去时间）
        timestamp_info_past = order_service.get_timestamp(-1)
        expected_diff_past = -1 * 86400  # -1天的秒数
        actual_diff_past = timestamp_info_past['after_days_sec'] - timestamp_info_past['sec']
        assert actual_diff_past == expected_diff_past
        
        # 测试无效输入
        with pytest.raises(TypeError):
            order_service.get_timestamp("invalid")
    
    def test_sign_login_message(self, order_service):
        """测试登录消息签名"""
        test_message = "Test login message"
        signature = order_service.sign_login_message(test_message)
        
        # 验证签名格式
        assert isinstance(signature, str)
        assert signature.startswith('0x')
        assert len(signature) == 132  # 0x + 64字节 = 132字符
    
    def test_strategy_info(self, order_service):
        """测试策略信息"""
        strategy_info = order_service.get_strategy_info()
        
        assert 'type' in strategy_info
        assert 'name' in strategy_info
        assert 'config' in strategy_info
        assert strategy_info['name'] == 'CurlCffiStrategy'
    
    def test_cookie_management(self, order_service):
        """测试 Cookie 管理"""
        # 测试设置 cookies
        test_cookies = {
            'test_cookie': 'test_value',
            'msu_wat': 'test_wat_token'
        }
        
        order_service.set_auth_cookies(test_cookies)
        
        # 测试获取 cookies
        cookies = order_service.get_auth_cookies()
        if cookies:  # 只有在支持 cookies 的策略下才测试
            assert 'test_cookie' in cookies
            assert cookies['test_cookie'] == 'test_value'
        
        # 测试清除 cookies
        order_service.clear_auth_cookies()
    
    def test_safety_checks(self, order_service):
        """测试安全检查"""
        params = {
            'token_amount': '1000000',
            'nft_token_id': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        # 测试没有确认参数时应该失败
        with pytest.raises(Exception) as exc_info:
            asyncio.run(order_service.place_limit_order(params))
        
        assert "安全检查" in str(exc_info.value)
        assert "confirm_real_order=True" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_strategy_switching(self, order_service):
        """测试策略切换"""
        original_strategy = order_service.get_strategy_info()['name']
        
        # 由于只有一个策略，这里主要测试切换逻辑不会出错
        try:
            await order_service.switch_strategy('curl_cffi', {'timeout': 20})
            new_strategy = order_service.get_strategy_info()['name']
            assert new_strategy == 'CurlCffiStrategy'
        except Exception as e:
            # 如果切换失败，确保是预期的错误
            assert "不支持的请求策略类型" in str(e) or "CurlCffiStrategy" in str(e)


@pytest.mark.asyncio
async def test_order_service_lifecycle():
    """测试订单服务生命周期"""
    test_private_key = "0x" + "2" * 64
    
    # 创建服务
    service = OrderService(test_private_key)
    
    # 初始化
    await service.init()
    
    # 验证初始化成功
    assert service.wallet_address is not None
    assert service.request_strategy is not None
    
    # 销毁服务
    await service.destroy()


def test_wallet_address_generation():
    """测试钱包地址生成"""
    test_private_key = "0x" + "3" * 64
    service = OrderService(test_private_key)
    
    # 验证地址格式
    assert service.wallet_address.startswith('0x')
    assert len(service.wallet_address) == 42
    
    # 验证相同私钥生成相同地址
    service2 = OrderService(test_private_key)
    assert service.wallet_address == service2.wallet_address


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])