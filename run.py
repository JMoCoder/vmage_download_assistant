#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号图片下载助手 - 启动脚本

这个脚本用于启动微信公众号图片下载助手应用。
它会检查依赖、创建必要的目录，并启动Flask应用。
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本是否满足要求"""
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"当前版本：{platform.python_version()}")
        sys.exit(1)
    else:
        print(f"✅ Python版本检查通过：{platform.python_version()}")

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        'flask',
        'flask_cors', 
        'requests',
        'beautifulsoup4',
        'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包：{', '.join(missing_packages)}")
        print("正在自动安装...")
        install_dependencies()
    else:
        print("✅ 所有依赖包检查通过")

def install_dependencies():
    """安装依赖包"""
    try:
        # 升级pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # 安装requirements.txt中的依赖
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败：{e}")
        print("\n请手动运行以下命令安装依赖：")
        print("pip install -r requirements.txt")
        sys.exit(1)

def create_directories():
    """创建必要的目录"""
    directories = [
        'downloads',
        'temp',
        'logs',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 目录创建/检查完成：{directory}")

def check_templates():
    """检查模板文件是否存在"""
    template_file = Path('templates/index.html')
    if not template_file.exists():
        print("❌ 模板文件不存在：templates/index.html")
        print("请确保项目文件完整")
        sys.exit(1)
    else:
        print("✅ 模板文件检查通过")

def setup_git_config():
    """设置Git配置，避免提交到GitHub"""
    try:
        # 检查是否已经是Git仓库
        if not Path('.git').exists():
            print("初始化Git仓库...")
            subprocess.run(['git', 'init'], check=True, capture_output=True)
        
        # 创建.gitignore文件
        gitignore_content = """# 微信公众号图片下载助手 - Git忽略文件

# Python相关
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# 虚拟环境
venv/
env/
ENV/

# IDE相关
.vscode/
.idea/
*.swp
*.swo
*~

# 项目特定文件
downloads/
temp/
logs/
*.log
*.zip

# 系统文件
.DS_Store
Thumbs.db

# 不提交到GitHub（用户要求）
.git/
*.git*
"""
        
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("✅ Git配置完成（已配置为不提交到GitHub）")
        
    except Exception as e:
        print(f"⚠️  Git配置警告：{e}")

def main():
    """主函数"""
    print("🚀 微信公众号图片下载助手启动检查")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖
    check_dependencies()
    
    # 创建目录
    create_directories()
    
    # 检查模板文件
    check_templates()
    
    # 设置Git配置
    setup_git_config()
    
    print("\n" + "=" * 50)
    print("✅ 启动检查完成，正在启动应用...")
    print("🌐 应用将在以下地址运行：")
    print("   本地访问：http://127.0.0.1:5000")
    print("   局域网访问：http://0.0.0.0:5000")
    print("\n💡 使用说明：")
    print("   1. 在浏览器中打开上述地址")
    print("   2. 输入微信公众号文章链接")
    print("   3. 点击'开始分析'按钮")
    print("   4. 选择需要下载的图片")
    print("   5. 点击'下载选中图片'")
    print("\n按Ctrl+C停止应用")
    print("=" * 50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(
            debug=True,  # 开发模式
            host='0.0.0.0',  # 允许外部访问
            port=5000,  # 端口号
            threaded=True  # 启用多线程
        )
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止，感谢使用!")
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("请检查app.py文件是否存在且正确")

if __name__ == '__main__':
    main() 