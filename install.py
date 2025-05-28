#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安装脚本，用于安装依赖和创建必要的目录
"""
import os
import subprocess
import sys


def ensure_directory(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def install_dependencies():
    """安装依赖"""
    try:
        # 尝试使用pip3安装
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装成功")
    except subprocess.CalledProcessError:
        print("安装依赖失败，请手动安装依赖:")
        print("pip install -r requirements.txt")
        return False
    return True


def create_directory_structure():
    """创建必要的目录结构"""
    # 创建报告和日志目录
    ensure_directory("reports")
    ensure_directory("logs")
    
    # 创建插件模板目录
    ensure_directory(os.path.join("disttest", "plugins", "templates"))
    
    print("目录结构创建完成")


def main():
    """主函数"""
    print("开始安装分布式测试框架...")
    
    # 创建目录结构
    create_directory_structure()
    
    # 安装依赖
    if install_dependencies():
        print("\n安装完成！您现在可以运行示例测试:")
        print("python examples/sample_test.py --mode=local")
        print("或")
        print("python examples/sample_test.py --mode=distributed")
    else:
        print("\n安装部分完成。请手动安装依赖后再运行示例测试。")


if __name__ == "__main__":
    main() 