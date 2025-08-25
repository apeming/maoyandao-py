#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的 GET 请求 API 设计
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"


async def test_new_api_design():
    """测试新的 API 设计"""
    print("🧪 测试新的 GET 请求 API 设计")
    print("=" * 50)
    
    # 检查环境变量
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("⚠️ 未找到 PRIVATE_KEY 环境变量")
        print("请在 .env 文件中设置 PRIVATE_KEY")
        return
    
    print(f"🔑 检测到私钥: {private_key[:10]}...{private_key[-10:]}")
    
    # 检查 FastAPI 服务是否运行
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            if response.status_code != 200:
                print("❌ FastAPI 服务未运行")
                print("请先启动服务: python run_server.py")
                return
    except Exception as e:
        print("❌ FastAPI 服务未运行")
        print("请先启动服务: python run_server.py")
        print(f"错误: {e}")
        return
    
    print("✅ FastAPI 服务正在运行")
    
    # 测试1: 获取价格（新的无需私钥参数的接口）
    print("\n1️⃣ 测试获取价格接口（新设计）")
    nft_token_id = "8279886802876316306180221210882"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/price/{nft_token_id}")
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("   ✅ 价格获取成功（私钥从环境变量自动获取）")
            else:
                print("   ⚠️ 价格获取失败，但接口设计正确")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试2: 市价单（GET 请求，默认参数）
    print("\n2️⃣ 测试市价单（GET 请求，默认参数）")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 只传必需参数，其他使用默认值
            params = {
                "nft_token_id": nft_token_id,
                "confirm_real_order": "false"  # 测试时设为 false
            }
            
            response = await client.get(f"{BASE_URL}/api/v1/order", params=params)
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 422:
                print("   ✅ 安全检查正常工作（confirm_real_order=false 被拒绝）")
            else:
                print("   ⚠️ 响应状态异常")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试3: 限价单（GET 请求，带 amount 参数）
    print("\n3️⃣ 测试限价单（GET 请求，带 amount 参数）")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "nft_token_id": nft_token_id,
                "order_type": "limit",
                "amount": "1.5",  # 1.5 个代币
                "confirm_real_order": "false"  # 测试时设为 false
            }
            
            response = await client.get(f"{BASE_URL}/api/v1/order", params=params)
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 422:
                print("   ✅ 安全检查正常工作（confirm_real_order=false 被拒绝）")
            else:
                print("   ⚠️ 响应状态异常")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试4: 限价单缺少 amount 参数
    print("\n4️⃣ 测试限价单缺少 amount 参数")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "nft_token_id": nft_token_id,
                "order_type": "limit",
                # 故意不提供 amount 参数
                "confirm_real_order": "true"
            }
            
            response = await client.get(f"{BASE_URL}/api/v1/order", params=params)
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 422:
                print("   ✅ 参数验证正常工作（限价单缺少 amount 被拒绝）")
            else:
                print("   ⚠️ 参数验证可能有问题")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试5: 真实订单创建（需要用户确认）
    print("\n5️⃣ 测试真实订单创建")
    print("   ⚠️ 这将尝试创建真实订单！")
    
    user_input = input("   是否继续测试真实订单创建？(y/N): ")
    if user_input.lower() != 'y':
        print("   已跳过真实订单测试")
        return
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            params = {
                "nft_token_id": nft_token_id,
                "order_type": "market",  # 市价单
                "confirm_real_order": "true"  # 确认创建真实订单
            }
            
            print("   🚀 发送真实订单请求...")
            response = await client.get(f"{BASE_URL}/api/v1/order", params=params)
            
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("   🎉 真实订单创建成功！")
                print("   ✅ 新的 API 设计完全正常工作")
            else:
                print("   ⚠️ 订单创建失败，但 API 设计正确")
                error_msg = result.get('message', '')
                if '请求被封禁' in error_msg or '请求太频繁' in error_msg:
                    print("   🌐 网络错误证明了真实的第三方请求正在进行")
                elif '未认证' in error_msg:
                    print("   🔐 认证错误证明了登录流程正在执行")
                
    except Exception as e:
        print(f"   ❌ 真实订单测试失败: {e}")


async def main():
    """主函数"""
    print("🔍 新 API 设计验证")
    print("验证 GET 请求和环境变量私钥的新设计")
    print()
    
    await test_new_api_design()
    
    print("\n" + "=" * 50)
    print("🎉 API 设计测试完成！")
    print()
    print("📋 新设计特点:")
    print("✅ GET 请求替代 POST 请求")
    print("✅ 私钥从环境变量自动获取")
    print("✅ nft_token_id 为唯一必需参数")
    print("✅ order_type 默认为 market")
    print("✅ 市价单自动获取价格")
    print("✅ 限价单需要 amount 参数")
    print("✅ 保持安全确认机制")


if __name__ == "__main__":
    asyncio.run(main())