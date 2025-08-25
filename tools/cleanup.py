#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目清理工具
清理临时文件、缓存文件和不需要的文件
"""

import os
import shutil
import glob
from pathlib import Path


def clean_pycache():
    """清理 Python 缓存文件"""
    print("🧹 清理 Python 缓存文件...")
    
    # 查找所有 __pycache__ 目录
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    
    # 删除 __pycache__ 目录
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"   删除: {pycache_dir}")
        except Exception as e:
            print(f"   ❌ 删除失败 {pycache_dir}: {e}")
    
    # 清理 .pyc 文件
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"   删除: {pyc_file}")
        except Exception as e:
            print(f"   ❌ 删除失败 {pyc_file}: {e}")
    
    print(f"✅ 清理了 {len(pycache_dirs)} 个缓存目录和 {len(pyc_files)} 个 .pyc 文件")


def clean_logs():
    """清理日志文件"""
    print("\n📝 清理日志文件...")
    
    log_files = glob.glob('**/*.log', recursive=True)
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"   删除: {log_file}")
        except Exception as e:
            print(f"   ❌ 删除失败 {log_file}: {e}")
    
    print(f"✅ 清理了 {len(log_files)} 个日志文件")


def clean_temp_files():
    """清理临时文件"""
    print("\n🗂️ 清理临时文件...")
    
    temp_patterns = [
        '**/.tmp',
        '**/.cache',
        '**/Thumbs.db',
        '**/.DS_Store',
        '**/*.swp',
        '**/*.swo',
        '**/*~'
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        temp_files = glob.glob(pattern, recursive=True)
        for temp_file in temp_files:
            try:
                if os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                else:
                    os.remove(temp_file)
                print(f"   删除: {temp_file}")
                cleaned_count += 1
            except Exception as e:
                print(f"   ❌ 删除失败 {temp_file}: {e}")
    
    print(f"✅ 清理了 {cleaned_count} 个临时文件")


def clean_test_artifacts():
    """清理测试产生的文件"""
    print("\n🧪 清理测试文件...")
    
    test_patterns = [
        '.coverage',
        'htmlcov/',
        '.pytest_cache/',
        '.tox/',
        'coverage.xml'
    ]
    
    cleaned_count = 0
    for pattern in test_patterns:
        if os.path.exists(pattern):
            try:
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                else:
                    os.remove(pattern)
                print(f"   删除: {pattern}")
                cleaned_count += 1
            except Exception as e:
                print(f"   ❌ 删除失败 {pattern}: {e}")
    
    print(f"✅ 清理了 {cleaned_count} 个测试文件")


def organize_files():
    """整理文件结构"""
    print("\n📁 检查文件组织...")
    
    # 检查是否有文件在错误的位置
    issues = []
    
    # 检查根目录是否有测试文件
    root_files = os.listdir('.')
    for file in root_files:
        if file.startswith('test_') and file.endswith('.py'):
            issues.append(f"测试文件 {file} 应该在 tests/ 目录中")
        elif file.startswith('example_') and file.endswith('.py'):
            issues.append(f"示例文件 {file} 应该在 examples/ 目录中")
    
    if issues:
        print("   发现以下组织问题:")
        for issue in issues:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ 文件组织良好")


def show_project_stats():
    """显示项目统计信息"""
    print("\n📊 项目统计:")
    
    # 统计不同类型的文件
    stats = {
        'Python 文件': len(glob.glob('**/*.py', recursive=True)),
        'Markdown 文档': len(glob.glob('**/*.md', recursive=True)),
        'JSON 配置': len(glob.glob('**/*.json', recursive=True)),
        'YAML 配置': len(glob.glob('**/*.yml', recursive=True)) + len(glob.glob('**/*.yaml', recursive=True)),
        '示例文件': len(glob.glob('examples/*.py', recursive=True)),
        '测试文件': len(glob.glob('tests/*.py', recursive=True)),
    }
    
    for file_type, count in stats.items():
        print(f"   {file_type}: {count}")
    
    # 统计目录
    important_dirs = ['app', 'tests', 'examples', 'docs', 'request_strategies']
    print("\n📂 重要目录:")
    for dir_name in important_dirs:
        if os.path.exists(dir_name):
            file_count = len([f for f in glob.glob(f'{dir_name}/**/*', recursive=True) if os.path.isfile(f)])
            print(f"   {dir_name}/: {file_count} 个文件")


def main():
    """主函数"""
    print("🧹 项目清理工具")
    print("=" * 50)
    
    # 确保在项目根目录
    if not os.path.exists('app') or not os.path.exists('order_service.py'):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 执行清理操作
    clean_pycache()
    clean_logs()
    clean_temp_files()
    clean_test_artifacts()
    organize_files()
    show_project_stats()
    
    print("\n✅ 项目清理完成！")


if __name__ == "__main__":
    main()