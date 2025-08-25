#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 订单服务使用示例
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# API 基础 URL
BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()


async def test_get_price():
    """测试获取价格接口"""
    print("💰 测试获取价格接口...")
    
    nft_token_id = "8279886802876316306180221210882"
    private_key = os.getenv('PRIVATE_KEY')
    
    if not private_key:
        print("❌ 未找到 PRIVATE_KEY 环境变量")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/price/{nft_token_id}",
            params={"private_key": private_key}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()


async def test_create_market_order():
    """测试创建市价单"""
    print("🛒 测试创建市价单...")
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ 未找到 PRIVATE_KEY 环境变量")
        return
    
    # 订单请求数据
    order_data = {
        "nft_token_id": "8279886802876316306180221210882",
        "order_type": "market",
        "private_key": private_key,
        "amount": 10,  # 10 个代币
        "confirm_real_order": True  # 确认下真实订单
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/order",
            json=order_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print()


async def test_create_limit_order():
    """测试创建限价单"""
    print("📋 测试创建限价单...")
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ 未找到 PRIVATE_KEY 环境变量")
        return
    
    # 订单请求数据
    order_data = {
        "nft_token_id": "8279886802876316306180221210882",
        "order_type": "limit",
        "private_key": private_key,
        "token_amount": "1000000000000000000",  # 1 个代币的 wei 数量
        "confirm_real_order": True  # 确认下真实订单
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/order",
            json=order_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print()


async def test_security_check():
    """测试安全检查机制"""
    print("🛡️ 测试安全检查机制...")
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ 未找到 PRIVATE_KEY 环境变量")
        return
    
    # 不设置 confirm_real_order 的订单请求
    order_data = {
        "nft_token_id": "8279886802876316306180221210882",
        "order_type": "market",
        "private_key": private_key,
        "amount": 10,
        "confirm_real_order": False  # 故意设置为 False 测试安全检查
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/order",
            json=order_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print()


async def main():
    """主测试函数"""
    print("🚀 开始测试 FastAPI 订单服务...")
    print("=" * 50)
    
    try:
        # 测试健康检查
        await test_health_check()
        
        # 测试获取价格
        await test_get_price()
        
        # 测试安全检查
        await test_security_check()
        
        # 注意：以下测试会创建真实订单，请谨慎使用
        print("⚠️  以下测试将创建真实订单，请确认后继续...")
        user_input = input("是否继续测试真实订单创建？(y/N): ")
        
        if user_input.lower() == 'y':
            # 测试创建市价单
            await test_create_market_order()
            
            # 测试创建限价单
            await test_create_limit_order()
        else:
            print("跳过真实订单测试")
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    print("✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main())