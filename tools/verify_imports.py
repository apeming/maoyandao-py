#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导入验证工具
验证所有模块的导入是否正常工作
"""

import sys
import os
import importlib
from typing import List, Tuple

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_import(module_path: str, description: str) -> Tuple[bool, str]:
    """
    测试模块导入
    
    Args:
        module_path: 模块路径
        description: 描述
        
    Returns:
        (是否成功, 错误信息)
    """
    try:
        importlib.import_module(module_path)
        return True, ""
    except Exception as e:
        return False, str(e)


def main():
    """主函数"""
    print("🔍 导入验证工具")
    print("=" * 50)
    
    # 定义要测试的导入
    imports_to_test = [
        # 向后兼容导入
        ("order_service", "向后兼容的 OrderService 导入"),
        
        # 核心模块导入
        ("app.core.order_service", "核心 OrderService 模块"),
        ("app.core.request_strategies.strategy_factory", "请求策略工厂"),
        ("app.core.request_strategies.curl_cffi_strategy", "curl_cffi 策略"),
        ("app.core.request_strategies.proxy_manager", "代理管理器"),
        ("app.core.request_strategies.base_request_strategy", "基础请求策略"),
        
        # FastAPI 应用模块
        ("app.main", "FastAPI 应用主模块"),
        ("app.core.config", "应用配置"),
        ("app.models.order", "订单数据模型"),
        ("app.services.order_service_wrapper", "订单服务包装器"),
        ("app.api.v1.order", "订单 API 路由"),
        ("app.api.v1.health", "健康检查 API 路由"),
    ]
    
    success_count = 0
    total_count = len(imports_to_test)
    
    print("📦 测试模块导入...")
    print()
    
    for module_path, description in imports_to_test:
        success, error = test_import(module_path, description)
        
        if success:
            print(f"✅ {description}")
            print(f"   模块: {module_path}")
            success_count += 1
        else:
            print(f"❌ {description}")
            print(f"   模块: {module_path}")
            print(f"   错误: {error}")
        print()
    
    # 显示结果
    print("=" * 50)
    print(f"📊 导入测试结果: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 所有模块导入成功！")
        
        # 测试具体的类导入
        print("\n🔧 测试具体类导入...")
        
        try:
            from order_service import OrderService
            print("✅ OrderService (向后兼容)")
            
            from app.core.order_service import OrderService as CoreOrderService
            print("✅ OrderService (核心模块)")
            
            from app.core.request_strategies.strategy_factory import RequestStrategyFactory
            print("✅ RequestStrategyFactory")
            
            from app.services.order_service_wrapper import OrderServiceWrapper
            print("✅ OrderServiceWrapper")
            
            from app.models.order import OrderRequest, OrderResponse
            print("✅ OrderRequest, OrderResponse")
            
            print("\n🎯 所有关键类导入成功！")
            
        except Exception as e:
            print(f"\n❌ 类导入测试失败: {e}")
            return 1
        
        return 0
    else:
        print(f"❌ {total_count - success_count} 个模块导入失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)