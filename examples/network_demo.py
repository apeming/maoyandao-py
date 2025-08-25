#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络请求演示脚本
展示项目中实际的第三方网络请求功能
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.order_service import OrderService


async def demo_network_requests():
    """演示实际的网络请求功能"""
    print("🌐 网络请求功能演示")
    print("=" * 50)
    
    # 使用测试私钥（不会进行真实交易）
    test_private_key = "0x" + "1" * 64
    
    # 创建订单服务实例
    service = OrderService(test_private_key, {
        'use_proxy': False,  # 演示时不使用代理
        'timeout': 10
    })
    
    try:
        await service.init()
        print(f"✅ 服务初始化成功")
        print(f"📡 使用请求策略: {service.get_strategy_info()['name']}")
        print(f"🔑 钱包地址: {service.wallet_address}")
        print()
        
        # 1. 演示获取商品详情（真实 API 请求）
        print("1️⃣ 获取商品详情")
        print("   API: GET https://msu.io/marketplace/api/marketplace/items/{token_id}")
        
        nft_token_id = '8279886802876316306180221210882'
        try:
            item_details = await service.get_item_details(nft_token_id)
            print(f"   ✅ 请求成功！")
            print(f"   📦 商品名称: {item_details.get('name', 'N/A')}")
            print(f"   💰 价格信息: {item_details.get('salesInfo', {}).get('priceWei', 'N/A')} wei")
            print(f"   🏷️ 商品ID: {item_details.get('id', 'N/A')}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        print()
        
        # 2. 演示获取商品价格（真实 API 请求）
        print("2️⃣ 获取商品价格")
        try:
            price = await service.get_item_price(nft_token_id)
            if price:
                print(f"   ✅ 商品当前价格: {price} wei")
                # 转换为更易读的格式
                price_eth = int(price) / 1_000_000_000_000_000_000
                print(f"   💎 价格 (ETH): {price_eth:.6f} ETH")
            else:
                print(f"   ℹ️ 商品当前不在售")
        except Exception as e:
            print(f"   ❌ 获取价格失败: {e}")
        
        print()
        
        # 3. 演示获取登录消息（真实 API 请求）
        print("3️⃣ 获取登录消息")
        print("   API: POST https://msu.io/swapnwarp/api/web/message")
        try:
            login_message = await service.get_login_message()
            print(f"   ✅ 获取登录消息成功！")
            print(f"   📝 消息内容: {login_message[:50]}...")
            print(f"   📏 消息长度: {len(login_message)} 字符")
        except Exception as e:
            print(f"   ❌ 获取登录消息失败: {e}")
        
        print()
        
        # 4. 演示请求策略信息
        print("4️⃣ 请求策略信息")
        strategy_info = service.get_strategy_info()
        print(f"   📡 策略类型: {strategy_info['type']}")
        print(f"   🏷️ 策略名称: {strategy_info['name']}")
        print(f"   ⚙️ 配置信息: {strategy_info['config']}")
        
        # 5. 演示代理信息
        print("\n5️⃣ 代理配置信息")
        proxy_info = service.get_proxy_info()
        print(f"   🔄 使用代理: {'是' if proxy_info['use_proxy'] else '否'}")
        print(f"   📊 代理数量: {proxy_info['proxy_count']}")
        print(f"   ✅ 代理可用: {'是' if proxy_info['proxy_available'] else '否'}")
        
        print()
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await service.destroy()
        print("🧹 资源清理完成")


async def demo_login_flow():
    """演示完整的登录流程（需要真实私钥）"""
    print("\n" + "=" * 50)
    print("🔐 登录流程演示")
    print("=" * 50)
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("⚠️ 跳过登录演示（未配置 PRIVATE_KEY 环境变量）")
        print("   如需测试登录功能，请在 .env 文件中设置 PRIVATE_KEY")
        return
    
    print("🔑 使用真实私钥进行登录演示...")
    service = OrderService(private_key, {
        'use_proxy': False,
        'timeout': 15
    })
    
    try:
        await service.init()
        print(f"✅ 服务初始化成功")
        print(f"🔑 钱包地址: {service.wallet_address}")
        
        # 步骤1: 获取登录消息
        print("\n📝 步骤1: 获取登录消息")
        login_message = await service.get_login_message()
        print(f"   ✅ 获取成功: {login_message[:30]}...")
        
        # 步骤2: 签名登录消息
        print("\n✍️ 步骤2: 签名登录消息")
        signature = service.sign_login_message(login_message)
        print(f"   ✅ 签名成功: {signature[:20]}...{signature[-20:]}")
        
        # 步骤3: 执行登录
        print("\n🚀 步骤3: 执行登录")
        print("   API: POST https://msu.io/swapnwarp/api/web/signin-wallet")
        login_response = await service.login()
        
        if login_response.get('success'):
            print("   ✅ 登录成功！")
            
            # 检查认证状态
            if service.is_authenticated():
                print("   🎉 认证状态: 已认证")
                
                # 显示认证信息（部分）
                auth_cookies = service.get_auth_cookies()
                if auth_cookies:
                    print("   🍪 认证 Cookies:")
                    for name, value in auth_cookies.items():
                        print(f"      {name}: {value[:15]}...")
            else:
                print("   ⚠️ 认证状态: 未认证")
        else:
            print(f"   ❌ 登录失败: {login_response}")
        
    except Exception as e:
        print(f"❌ 登录演示失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.destroy()


async def demo_order_creation():
    """演示订单创建和签名（不提交真实订单）"""
    print("\n" + "=" * 50)
    print("📋 订单创建演示")
    print("=" * 50)
    
    test_private_key = "0x" + "2" * 64
    service = OrderService(test_private_key)
    
    try:
        await service.init()
        print(f"✅ 服务初始化成功")
        
        # 订单参数
        order_params = {
            'nft_token_id': '8279886802876316306180221210882',
            'token_amount': '1000000000000000000'  # 1 ETH in wei
        }
        
        print(f"\n📦 订单参数:")
        print(f"   NFT Token ID: {order_params['nft_token_id']}")
        print(f"   Token Amount: {order_params['token_amount']} wei")
        
        # 创建限价单
        print(f"\n📋 创建限价单...")
        limit_order = service.create_limit_order(order_params)
        print(f"   ✅ 限价单创建成功")
        print(f"   📄 订单数据:")
        for key, value in limit_order.items():
            print(f"      {key}: {value}")
        
        # 签名订单
        print(f"\n✍️ 签名订单...")
        signature = service.sign_order(limit_order)
        print(f"   ✅ 签名成功: {signature[:20]}...{signature[-20:]}")
        
        # 创建市价单
        print(f"\n🛒 创建市价单...")
        market_order = service.create_market_order(order_params)
        print(f"   ✅ 市价单创建成功")
        
        market_signature = service.sign_order(market_order)
        print(f"   ✅ 市价单签名: {market_signature[:20]}...{market_signature[-20:]}")
        
        print(f"\n💡 注意: 以上只是创建和签名订单，没有提交到网络")
        print(f"   真实下单需要设置 confirm_real_order=True 并完成登录认证")
        
    except Exception as e:
        print(f"❌ 订单创建演示失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.destroy()


async def main():
    """主函数"""
    print("🚀 订单服务网络功能完整演示")
    print("展示项目中实际的第三方网络请求功能")
    print()
    
    # 演示基本网络请求
    await demo_network_requests()
    
    # 演示登录流程
    await demo_login_flow()
    
    # 演示订单创建
    await demo_order_creation()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print()
    print("📋 总结:")
    print("✅ 项目确实包含完整的第三方网络请求实现")
    print("✅ 使用 curl_cffi 库进行真实的 HTTP 请求")
    print("✅ 与 https://msu.io 网站进行实际交互")
    print("✅ 支持代理、Cookie 管理、错误处理等高级功能")
    print("✅ 包含完整的登录认证和订单提交流程")


if __name__ == "__main__":
    asyncio.run(main())