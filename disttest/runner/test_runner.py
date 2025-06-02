"""
TestRunner类 - 测试运行器
支持本地和分布式测试执行
"""
import concurrent.futures
import os
import socket
import time
import uuid
import math
from typing import Dict, List, Type, Any, Optional, Tuple

from ..core import TestCase, TestSuite, TestResult
from .node_manager import NodeManager
from ..plugins.base import PluginBase


class TestRunner:
    """测试运行器，负责执行测试并收集结果"""
    
    def __init__(self):
        self.test_suite = TestSuite()
        self.plugins: List[PluginBase] = []
        self.node_manager = NodeManager()
        self.master_node_id = f"{socket.gethostname()}-{os.getpid()}"
        self.running_nodes: Dict[str, Dict[str, Any]] = {}
        self.merged_results = TestResult()
        self.merged_results.node_id = self.master_node_id
    
    def add_test_case(self, test_case_class: Type[TestCase]) -> None:
        """添加单个测试用例类"""
        self.test_suite.add_test_case(test_case_class)
    
    def add_test_cases(self, test_case_classes: List[Type[TestCase]]) -> None:
        """批量添加多个测试用例类"""
        self.test_suite.add_test_cases(test_case_classes)
    
    def add_plugin(self, plugin: PluginBase) -> None:
        """添加插件"""
        self.plugins.append(plugin)
        plugin.setup(self)
    
    def run_local(self) -> TestResult:
        """在本地执行测试"""
        print(f"在本地节点 {self.master_node_id} 上开始执行测试...")
        
        # 重置结果
        self.merged_results = TestResult()
        self.merged_results.node_id = self.master_node_id
        
        # 触发测试开始事件
        for plugin in self.plugins:
            plugin.on_test_run_start(self.test_suite)
        
        # 执行测试
        result = self.test_suite.run(self.master_node_id)
        self.merged_results.merge(result)
        
        # 触发测试完成事件
        for plugin in self.plugins:
            plugin.on_test_run_complete(self.merged_results)
        
        summary = result.get_summary()
        print(f"测试执行完成. 总测试用例数: {summary['total']}, 通过: {summary['passed']}, 失败: {summary['failed']}")
        return self.merged_results
    
    def run_distributed(self, nodes: int = 2, timeout: float = 600) -> TestResult:
        """分布式执行测试
        
        Args:
            nodes: 并行执行的节点数
            timeout: 测试执行超时时间（秒）
            
        Returns:
            合并后的测试结果
        """
        print(f"开始分布式测试执行，节点数量: {nodes}")
        
        # 重置结果
        self.merged_results = TestResult()
        self.merged_results.node_id = self.master_node_id
        
        # 触发测试开始事件
        for plugin in self.plugins:
            plugin.on_test_run_start(self.test_suite)
            
        # 获取所有测试用例
        all_test_cases = self.test_suite.test_cases.copy()
        total_tests = len(all_test_cases)
        
        # 如果节点数量大于测试用例类数量，调整节点数量
        if nodes > total_tests:
            nodes = max(1, total_tests)
            print(f"警告: 节点数量({nodes})大于测试用例类数量({total_tests})，调整节点数量为: {nodes}")
        
        # 将测试用例分配到各个节点
        node_ids = [f"node-{i+1}-{uuid.uuid4().hex[:8]}" for i in range(nodes)]
        node_test_cases = self._distribute_test_cases(all_test_cases, nodes)
        
        print(f"总测试用例类数量: {total_tests}, 分配到 {nodes} 个节点执行")
        
        # 使用线程池模拟分布式执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=nodes) as executor:
            futures = []
            for i, node_id in enumerate(node_ids):
                # 在每个"节点"上运行分配的测试用例
                node_tests = node_test_cases[i]
                futures.append(executor.submit(self._run_on_node, node_id, node_tests))
            
            # 等待所有节点完成并获取结果
            for future in concurrent.futures.as_completed(futures):
                try:
                    node_result = future.result()
                    self.merged_results.merge(node_result)
                    # 实时汇总结果后触发进度更新事件
                    for plugin in self.plugins:
                        plugin.on_test_progress_update(self.merged_results)
                except Exception as e:
                    print(f"节点执行测试时出错: {str(e)}")
        
        self.merged_results.set_complete()
        
        # 触发测试完成事件
        for plugin in self.plugins:
            plugin.on_test_run_complete(self.merged_results)
            
        summary = self.merged_results.get_summary()
        print(f"分布式测试执行完成. 总测试用例数: {summary['total']}, "
              f"通过: {summary['passed']}, 失败: {summary['failed']}, "
              f"通过率: {summary['pass_rate'] * 100:.2f}%")
              
        return self.merged_results
    
    def _distribute_test_cases(self, test_cases: List[Type[TestCase]], nodes: int) -> List[List[Type[TestCase]]]:
        """将测试用例分配到各个节点
        
        Args:
            test_cases: 所有测试用例
            nodes: 节点数量
            
        Returns:
            分配到各个节点的测试用例列表
        """
        # 计算每个节点分配的测试用例数量
        total = len(test_cases)
        base_count = total // nodes
        remainder = total % nodes
        
        # 分配测试用例
        result = []
        start_idx = 0
        
        for i in range(nodes):
            # 计算当前节点的测试用例数量
            count = base_count + (1 if i < remainder else 0)
            end_idx = start_idx + count
            
            # 分配测试用例
            node_tests = test_cases[start_idx:end_idx]
            result.append(node_tests)
            
            # 更新起始索引
            start_idx = end_idx
            
            # 计算每个节点的测试方法数
            method_count = 0
            for test_class in node_tests:
                method_count += len(test_class.get_test_methods())
            
            print(f"节点 {i+1}: 分配了 {len(node_tests)} 个测试用例类, {method_count} 个测试用例")
        
        return result
    
    def _run_on_node(self, node_id: str, test_cases: List[Type[TestCase]]) -> TestResult:
        """在单个节点上执行测试套件
        
        这是一个内部方法，模拟在远程节点上执行测试
        在实际的分布式环境中，这里应该是与远程节点通信的代码
        """
        # 计算测试方法数
        method_count = 0
        for test_class in test_cases:
            method_count += len(test_class.get_test_methods())
            
        print(f"节点 {node_id} 开始执行 {len(test_cases)} 个测试用例类 ({method_count} 个测试用例)...")
        
        # 创建节点的测试套件
        node_suite = TestSuite(f"{self.test_suite.name}-{node_id}")
        node_suite.test_cases = test_cases
        
        # 触发节点开始事件
        for plugin in self.plugins:
            plugin.on_node_start(node_id, node_suite)
        
        # 执行测试
        result = node_suite.run(node_id)
        
        # 设置节点ID
        result.node_id = node_id
        
        # 触发节点完成事件
        for plugin in self.plugins:
            plugin.on_node_complete(node_id, result)
        
        summary = result.get_summary()
        print(f"节点 {node_id} 测试执行完成. 执行了 {summary['total']} 个测试用例, 通过: {summary['passed']}, 失败: {summary['failed']}")
        return result 