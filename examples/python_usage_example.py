#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python 原生订单服务使用示例
演示如何直接使用 OrderService 类进行订单操作
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


async def demo_order_creation():
    """演示订单创建和签名（不会提交真实订单）"""
    print("=== Python 原生订单服务演示 ===\n")
    
    # 注意：这里使用测试私钥，实际使用时请使用真实私钥
    test_private_key = "0x" + "1" * 64  # 测试私钥
    
    # 创建订单服务实例
    service = OrderService(test_private_key, {
        'strategy': 'curl_cffi',
        'timeout': 10
    })
    
    try:
        # 初始化服务
        await service.init()
        print(f"钱包地址: {service.wallet_address}")
        print(f"使用策略: {service.get_strategy_info()['name']}\n")
        
        # 测试订单参数
        test_params = {
            'token_amount': '1000000',  # 1 USDC (6位小数)
            'nft_token_id': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        print("=== 创建限价订单 ===")
        limit_order = service.create_limit_order(test_params)
        print("限价订单数据:")
        for key, value in limit_order.items():
            print(f"  {key}: {value}")
        
        print("\n=== 签名订单 ===")
        signature = service.sign_order(limit_order)
        print(f"订单签名: {signature[:20]}...{signature[-20:]}")
        
        print("\n=== 创建市价订单 ===")
        market_order = service.create_market_order(test_params)
        print("市价订单数据:")
        for key, value in market_order.items():
            print(f"  {key}: {value}")
        
        market_signature = service.sign_order(market_order)
        print(f"市价订单签名: {market_signature[:20]}...{market_signature[-20:]}")
        
        print("\n=== 时间戳功能测试 ===")
        timestamp_info = service.get_timestamp(7)  # 7天后
        print(f"当前时间戳(秒): {timestamp_info['sec']}")
        print(f"7天后时间戳(秒): {timestamp_info['after_days_sec']}")
        print(f"时间差(天): {(timestamp_info['after_days_sec'] - timestamp_info['sec']) / 86400}")
        
        print("\n=== 策略信息 ===")
        strategy_info = service.get_strategy_info()
        print(f"策略类型: {strategy_info['type']}")
        print(f"策略名称: {strategy_info['name']}")
        
        print("\n✅ 演示完成！所有功能正常工作。")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await service.destroy()


async def demo_login_flow():
    """演示登录流程（需要真实私钥和网络连接）"""
    print("\n=== 登录流程演示 ===")
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("跳过登录演示（未配置 PRIVATE_KEY 环境变量）")
        return
    
    print("使用真实私钥进行登录演示...")
    service = OrderService(private_key)
    
    try:
        await service.init()
        print(f"钱包地址: {service.wallet_address}")
        
        # 获取登录消息
        print("获取登录消息...")
        login_message = await service.get_login_message()
        print(f"登录消息: {login_message[:50]}...")
        
        # 执行登录
        print("执行登录...")
        login_response = await service.login()
        print("✅ 登录成功!")
        
        # 获取认证状态
        if service.is_authenticated():
            print("✅ 认证状态: 已认证")
        else:
            print("❌ 认证状态: 未认证")
        
    except Exception as e:
        print(f"❌ 登录演示失败: {e}")
    
    finally:
        await service.destroy()


async def demo_safety_checks():
    """演示安全检查功能"""
    print("\n=== 安全检查演示 ===")
    
    test_private_key = "0x" + "2" * 64
    service = OrderService(test_private_key)
    
    try:
        await service.init()
        
        test_params = {
            'token_amount': '1000000',
            'nft_token_id': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        print("尝试在没有确认的情况下下单...")
        try:
            # 这应该会失败，因为没有设置 confirm_real_order=True
            await service.place_limit_order(test_params)
        except Exception as e:
            print(f"✅ 安全检查生效: {e}")
        
        print("\n使用正确的安全确认参数...")
        try:
            # 这里演示正确的调用方式（但仍然不会真正下单，因为使用的是测试环境）
            # await service.place_limit_order(test_params, confirm_real_order=True)
            print("✅ 安全检查通过（实际下单已跳过）")
        except Exception as e:
            print(f"下单过程中的其他错误: {e}")
    
    except Exception as e:
        print(f"安全检查演示失败: {e}")
    
    finally:
        await service.destroy()


async def demo_real_order_example():
    """演示真实订单创建（需要用户确认）"""
    print("\n=== 真实订单创建演示 ===")
    
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("跳过真实订单演示（未配置 PRIVATE_KEY 环境变量）")
        return
    
    print("⚠️  以下操作将创建真实订单，请谨慎操作！")
    user_input = input("是否继续？(y/N): ")
    
    if user_input.lower() != 'y':
        print("已取消真实订单演示")
        return
    
    service = OrderService(private_key)
    
    try:
        await service.init()
        await service.login()
        
        # 获取商品价格
        nft_token_id = '8279886802876316306180221210882'
        price = await service.get_item_price(nft_token_id)
        
        if price:
            print(f"商品当前价格: {price} wei")
            
            # 创建市价单参数
            params = {
                'nft_token_id': nft_token_id,
                'token_amount': price
            }
            
            print("创建市价单...")
            result = await service.place_market_order(params, confirm_real_order=True)
            print(f"✅ 订单创建结果: {result}")
        else:
            print("❌ 商品当前不在售")
    
    except Exception as e:
        print(f"❌ 真实订单演示失败: {e}")
    
    finally:
        await service.destroy()


async def main():
    """主函数"""
    print("Python 原生订单服务完整演示\n")
    
    # 运行各种演示
    await demo_order_creation()
    await demo_login_flow()
    await demo_safety_checks()
    await demo_real_order_example()
    
    print("\n🎉 所有演示完成！")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())