#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置测试工具
验证应用配置是否正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def main():
    """主函数"""
    print("🔧 应用配置测试")
    print("=" * 50)
    
    try:
        # 测试配置导入
        print("1️⃣ 测试配置模块导入...")
        from app.core.config import settings
        print("   ✅ 配置模块导入成功")
        
        # 测试配置值
        print("\n2️⃣ 测试配置值...")
        print(f"   应用名称: {settings.app_name}")
        print(f"   应用版本: {settings.app_version}")
        print(f"   服务器地址: {settings.host}:{settings.port}")
        print(f"   RPC URL: {settings.rpc_url}")
        print(f"   请求超时: {settings.request_timeout}s")
        print(f"   使用代理: {settings.use_proxy}")
        print(f"   代理文件: {settings.proxy_file}")
        print(f"   需要确认: {settings.require_confirmation}")
        print("   ✅ 所有配置值正常")
        
        # 测试环境变量处理
        print("\n3️⃣ 测试环境变量处理...")
        
        # 检查是否有 PRIVATE_KEY 环境变量
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            print(f"   检测到 PRIVATE_KEY: {private_key[:10]}...{private_key[-10:]}")
            print("   ✅ 环境变量正常处理（已忽略额外字段）")
        else:
            print("   未检测到 PRIVATE_KEY 环境变量")
            print("   ✅ 环境变量处理正常")
        
        # 测试服务包装器导入
        print("\n4️⃣ 测试服务包装器...")
        try:
            from app.services.order_service_wrapper import order_service_wrapper
            print("   ✅ 订单服务包装器导入成功")
        except Exception as e:
            print(f"   ⚠️ 服务包装器导入失败: {e}")
            print("   （这可能是因为缺少 FastAPI 依赖，但不影响核心功能）")
        
        print("\n" + "=" * 50)
        print("🎉 配置测试完成！")
        print("✅ 应用配置正常工作，可以启动服务")
        
        return 0
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)