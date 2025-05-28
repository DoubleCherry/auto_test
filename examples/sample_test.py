#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例测试脚本，展示如何使用分布式测试框架
"""
import os
import sys
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from disttest.core import TestCase
from disttest.runner import TestRunner
from disttest.plugins import HTMLReportPlugin, ConsoleReporterPlugin, JSONLoggerPlugin


class MathTestCase(TestCase):
    """数学运算测试用例"""
    
    @classmethod
    def setup_class(cls):
        """类级别的前置处理"""
        print("MathTestCase 前置处理")
    
    def setup(self):
        """方法级别的前置处理"""
        super().setup()
        self.value = 10
    
    def test_addition(self):
        """测试加法运算"""
        # 模拟运算延迟
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.value + 5, 15)
    
    def test_subtraction(self):
        """测试减法运算"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.value - 5, 5)
    
    def test_multiplication(self):
        """测试乘法运算"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.value * 2, 20)
    
    def test_division(self):
        """测试除法运算"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.value / 2, 5)
    
    def teardown(self):
        """方法级别的后置处理"""
        super().teardown()
        self.value = None
    
    @classmethod
    def teardown_class(cls):
        """类级别的后置处理"""
        print("MathTestCase 后置处理")


class StringTestCase(TestCase):
    """字符串操作测试用例"""
    
    def setup(self):
        """方法级别的前置处理"""
        super().setup()
        self.test_string = "Hello, World!"
    
    def test_length(self):
        """测试字符串长度"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(len(self.test_string), 13)
    
    def test_uppercase(self):
        """测试字符串大写转换"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.test_string.upper(), "HELLO, WORLD!")
    
    def test_lowercase(self):
        """测试字符串小写转换"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.test_string.lower(), "hello, world!")
    
    def test_split(self):
        """测试字符串分割"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.test_string.split(", "), ["Hello", "World!"])
    
    def test_replace(self):
        """测试字符串替换"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.test_string.replace("Hello", "Hi"), "Hi, World!")
    
    def test_contains(self):
        """测试字符串包含"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_true("World" in self.test_string)
    
    def test_startswith(self):
        """测试字符串开头"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_true(self.test_string.startswith("Hello"))
    
    def test_endswith(self):
        """测试字符串结尾"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_true(self.test_string.endswith("!"))
        
    def test_failure_example(self):
        """故意失败的测试用例"""
        time.sleep(random.uniform(0.1, 0.5))
        self.assert_equal(self.test_string, "Wrong value")


def run_local_test():
    """本地运行测试"""
    runner = TestRunner()
    
    # 添加测试用例
    runner.add_test_case(MathTestCase)
    runner.add_test_case(StringTestCase)
    
    # 添加控制台报告插件
    runner.add_plugin(ConsoleReporterPlugin(verbose=True))
    
    # 运行测试
    result = runner.run_local()
    print(f"测试执行完成，总共 {result.get_summary()['total']} 个测试用例")


def run_distributed_test(nodes=3):
    """分布式运行测试"""
    runner = TestRunner()
    
    # 添加测试用例
    runner.add_test_case(MathTestCase)
    runner.add_test_case(StringTestCase)
    
    # 添加控制台报告插件
    runner.add_plugin(ConsoleReporterPlugin())
    
    # 添加HTML报告插件
    runner.add_plugin(HTMLReportPlugin())
    
    # 添加JSON日志插件
    runner.add_plugin(JSONLoggerPlugin())
    
    # 运行分布式测试
    result = runner.run_distributed(nodes=nodes)
    print(f"分布式测试执行完成，总共 {result.get_summary()['total']} 个测试用例")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="示例测试脚本")
    parser.add_argument("--mode", choices=["local", "distributed"], default="local",
                        help="运行模式：local (本地) 或 distributed (分布式)")
    parser.add_argument("--nodes", type=int, default=3, help="分布式模式下的节点数量")
    
    args = parser.parse_args()
    
    if args.mode == "local":
        print("以本地模式运行测试...")
        run_local_test()
    else:
        print(f"以分布式模式运行测试，节点数量: {args.nodes}...")
        run_distributed_test(nodes=args.nodes) 