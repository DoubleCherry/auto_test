#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行接口模块
"""
import argparse
import importlib
import os
import sys
from typing import List, Type

from .core import TestCase
from .runner import TestRunner
from .plugins import HTMLReportPlugin, ConsoleReporterPlugin, JSONLoggerPlugin


def import_test_case(module_path: str) -> List[Type[TestCase]]:
    """导入测试用例模块并获取所有TestCase子类
    
    Args:
        module_path: 模块路径 (例如: path.to.module)
        
    Returns:
        TestCase子类列表
    """
    try:
        module = importlib.import_module(module_path)
        test_cases = []
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, TestCase) and attr != TestCase:
                test_cases.append(attr)
                
        return test_cases
    except ImportError as e:
        print(f"错误: 无法导入模块 {module_path}: {e}")
        sys.exit(1)


def main():
    """命令行工具入口点"""
    parser = argparse.ArgumentParser(description="分布式测试框架命令行工具")
    parser.add_argument("test_modules", nargs="+", help="测试模块路径列表 (例如: path.to.module)")
    parser.add_argument("--mode", choices=["local", "distributed"], default="local",
                        help="运行模式: local (本地) 或 distributed (分布式) [默认: local]")
    parser.add_argument("--nodes", type=int, default=3, 
                        help="分布式模式下的节点数量 [默认: 3]")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="显示详细输出")
    parser.add_argument("--html-report", action="store_true", 
                        help="生成HTML报告")
    parser.add_argument("--report-dir", default="reports", 
                        help="报告输出目录 [默认: reports]")
    parser.add_argument("--json-log", action="store_true", 
                        help="生成JSON日志")
    parser.add_argument("--log-dir", default="logs", 
                        help="日志输出目录 [默认: logs]")
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 导入所有测试模块并添加测试用例
    for module_path in args.test_modules:
        test_cases = import_test_case(module_path)
        if not test_cases:
            print(f"警告: 在模块 {module_path} 中没有找到测试用例")
            continue
            
        print(f"从模块 {module_path} 中加载了 {len(test_cases)} 个测试用例")
        for test_case in test_cases:
            runner.add_test_case(test_case)
    
    # 添加控制台报告插件
    runner.add_plugin(ConsoleReporterPlugin(verbose=args.verbose))
    
    # 如果需要，添加HTML报告插件
    if args.html_report:
        runner.add_plugin(HTMLReportPlugin(output_dir=args.report_dir))
        
    # 如果需要，添加JSON日志插件
    if args.json_log:
        runner.add_plugin(JSONLoggerPlugin(log_dir=args.log_dir))
        
    # 运行测试
    if args.mode == "local":
        print("以本地模式运行测试...")
        result = runner.run_local()
    else:
        print(f"以分布式模式运行测试，节点数量: {args.nodes}...")
        result = runner.run_distributed(nodes=args.nodes)
        
    # 设置退出码
    summary = result.get_summary()
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 