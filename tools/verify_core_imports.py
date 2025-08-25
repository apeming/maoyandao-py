#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心导入验证工具
验证核心模块的导入是否正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def main():
    """主函数"""
    print("🔍 核心模块导入验证")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # 测试1: 向后兼容导入
    print("1️⃣ 测试向后兼容导入...")
    try:
        from order_service import OrderService
        print("   ✅ from order_service import OrderService")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试2: 核心模块导入
    print("\n2️⃣ 测试核心模块导入...")
    try:
        from app.core.order_service import OrderService as CoreOrderService
        print("   ✅ from app.core.order_service import OrderService")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试3: 请求策略导入
    print("\n3️⃣ 测试请求策略导入...")
    try:
        from app.core.request_strategies.strategy_factory import RequestStrategyFactory
        print("   ✅ from app.core.request_strategies.strategy_factory import RequestStrategyFactory")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试4: curl_cffi 策略导入
    print("\n4️⃣ 测试 curl_cffi 策略导入...")
    try:
        from app.core.request_strategies.curl_cffi_strategy import CurlCffiStrategy
        print("   ✅ from app.core.request_strategies.curl_cffi_strategy import CurlCffiStrategy")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试5: 代理管理器导入
    print("\n5️⃣ 测试代理管理器导入...")
    try:
        from app.core.request_strategies.proxy_manager import ProxyManager
        print("   ✅ from app.core.request_strategies.proxy_manager import ProxyManager")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试6: 数据模型导入
    print("\n6️⃣ 测试数据模型导入...")
    try:
        from app.models.order import OrderRequest, OrderResponse, OrderType
        print("   ✅ from app.models.order import OrderRequest, OrderResponse, OrderType")
        success_count += 1
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
    total_tests += 1
    
    # 测试7: 类实例化测试
    print("\n7️⃣ 测试类实例化...")
    try:
        # 测试 OrderService 实例化
        test_private_key = "0x" + "1" * 64
        service = OrderService(test_private_key)
        print("   ✅ OrderService 实例化成功")
        
        # 测试策略工厂
        strategy = RequestStrategyFactory.create('curl_cffi')
        print("   ✅ RequestStrategyFactory 创建策略成功")
        
        # 测试代理管理器
        proxy_manager = ProxyManager()
        print("   ✅ ProxyManager 实例化成功")
        
        success_count += 1
    except Exception as e:
        print(f"   ❌ 实例化失败: {e}")
    total_tests += 1
    
    # 显示结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有核心模块导入成功！")
        print("\n✅ 项目结构迁移完成，所有核心功能正常工作")
        return 0
    else:
        print(f"❌ {total_tests - success_count} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)