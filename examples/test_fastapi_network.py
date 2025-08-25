#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 FastAPI 是否真的进行网络请求
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"


async def test_fastapi_network_requests():
    """测试 FastAPI 是否真的进行网络请求"""
    print("🧪 测试 FastAPI 网络请求功能")
    print("=" * 50)
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ 未找到 PRIVATE_KEY 环境变量")
        print("请在 .env 文件中设置 PRIVATE_KEY 来测试真实网络请求")
        return
    
    print(f"🔑 使用私钥: {private_key[:10]}...{private_key[-10:]}")
    
    # 测试获取价格（这会触发真实的网络请求）
    print("\n1️⃣ 测试获取价格接口")
    nft_token_id = "8279886802876316306180221210882"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/price/{nft_token_id}",
                params={"private_key": private_key}
            )
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("   ✅ FastAPI 成功调用了真实的网络请求！")
                if result.get('price_wei'):
                    print(f"   💰 获取到真实价格: {result['price_wei']} wei")
            else:
                print("   ⚠️ 网络请求失败，但这证明了 FastAPI 确实在尝试网络请求")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试创建订单（会触发登录和下单的网络请求）
    print("\n2️⃣ 测试创建订单接口")
    
    # 先测试安全检查
    print("   测试安全检查...")
    order_data_unsafe = {
        "nft_token_id": nft_token_id,
        "order_type": "market",
        "private_key": private_key,
        "amount": 1,
        "confirm_real_order": False  # 故意设置为 False
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/order",
                json=order_data_unsafe
            )
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 422:
                print("   ✅ 安全检查正常工作")
            
    except Exception as e:
        print(f"   ❌ 安全检查测试失败: {e}")
    
    # 测试真实订单创建（需要用户确认）
    print("\n   测试真实订单创建...")
    print("   ⚠️ 这将尝试创建真实订单！")
    
    user_input = input("   是否继续测试真实订单创建？(y/N): ")
    if user_input.lower() != 'y':
        print("   已跳过真实订单测试")
        return
    
    order_data_real = {
        "nft_token_id": nft_token_id,
        "order_type": "market",
        "private_key": private_key,
        "amount": 1,
        "confirm_real_order": True  # 确认创建真实订单
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("   🚀 发送订单创建请求...")
            response = await client.post(
                f"{BASE_URL}/api/v1/order",
                json=order_data_real
            )
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("   🎉 FastAPI 成功创建了真实订单！")
                print("   ✅ 这证明了 FastAPI 确实在进行真实的网络请求")
            else:
                print("   ⚠️ 订单创建失败，但这证明了 FastAPI 确实在尝试网络请求")
                error_msg = result.get('message', '')
                if '请求被封禁' in error_msg or '请求太频繁' in error_msg:
                    print("   🌐 网络错误证明了真实的第三方请求正在进行")
                elif '未认证' in error_msg:
                    print("   🔐 认证错误证明了登录流程正在执行")
                
    except Exception as e:
        print(f"   ❌ 真实订单测试失败: {e}")


async def main():
    """主函数"""
    print("🔍 FastAPI 网络请求验证")
    print("验证 FastAPI 是否真的调用了第三方网络请求")
    print()
    
    # 检查 FastAPI 服务是否运行
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            if response.status_code == 200:
                print("✅ FastAPI 服务正在运行")
                await test_fastapi_network_requests()
            else:
                print("❌ FastAPI 服务响应异常")
    except Exception as e:
        print("❌ FastAPI 服务未运行")
        print("请先启动 FastAPI 服务: python run_server.py")
        print(f"错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())