#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号图片下载助手 - 安装测试脚本

用于验证项目环境是否正确配置
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """测试Python版本"""
    print("🔍 测试Python版本...")
    if sys.version_info >= (3, 8):
        print(f"✅ Python版本: {sys.version}")
        return True
    else:
        print(f"❌ Python版本过低: {sys.version}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n🔍 测试依赖包...")
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('requests', 'requests'),
        ('bs4', 'BeautifulSoup4'),
        ('PIL', 'Pillow'),
    ]
    
    success = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            success = False
    
    return success

def test_files():
    """测试项目文件"""
    print("\n🔍 测试项目文件...")
    
    required_files = [
        'app.py',
        'run.py',
        'requirements.txt',
        'README.md',
        'templates/index.html'
    ]
    
    success = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            success = False
    
    return success

def test_directories():
    """测试目录结构"""
    print("\n🔍 测试目录结构...")
    
    directories = ['downloads', 'temp', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    return True

def test_flask_import():
    """测试Flask应用导入"""
    print("\n🔍 测试Flask应用导入...")
    
    try:
        from app import app
        print("✅ Flask应用导入成功")
        return True
    except ImportError as e:
        print(f"❌ Flask应用导入失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Flask应用导入警告: {e}")
        return True

def main():
    """主测试函数"""
    print("🧪 微信公众号图片下载助手 - 环境测试")
    print("=" * 50)
    
    tests = [
        ("Python版本", test_python_version),
        ("依赖包", test_dependencies),
        ("项目文件", test_files),
        ("目录结构", test_directories),
        ("Flask应用", test_flask_import),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        result = test_func()
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！项目已准备就绪。")
        print("\n运行以下命令启动应用：")
        print("python run.py")
    else:
        print("💥 测试失败！请根据上述错误信息修复问题。")
        print("\n建议操作：")
        print("1. 安装缺失的依赖: pip install -r requirements.txt")
        print("2. 检查项目文件是否完整")
        print("3. 确保Python版本 >= 3.8")
    
    print("=" * 50)

if __name__ == '__main__':
    main() 