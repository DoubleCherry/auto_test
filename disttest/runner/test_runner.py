"""
TestRunner类 - 测试运行器
支持本地和分布式测试执行
"""
import concurrent.futures
import os
import socket
import time
import uuid
from typing import Dict, List, Type, Any, Optional

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
        
        # 触发测试开始事件
        for plugin in self.plugins:
            plugin.on_test_run_start(self.test_suite)
        
        # 执行测试
        result = self.test_suite.run(self.master_node_id)
        self.merged_results.merge(result)
        
        # 触发测试完成事件
        for plugin in self.plugins:
            plugin.on_test_run_complete(self.merged_results)
        
        print(f"测试执行完成. 总测试数: {result.get_summary()['total']}, 通过: {result.get_summary()['passed']}, 失败: {result.get_summary()['failed']}")
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
        
        # 触发测试开始事件
        for plugin in self.plugins:
            plugin.on_test_run_start(self.test_suite)
            
        # 将测试用例分配到各个节点
        total_tests = self.test_suite.get_total_test_count()
        node_ids = [f"node-{i+1}-{uuid.uuid4().hex[:8]}" for i in range(nodes)]
        
        print(f"总测试用例数: {total_tests}, 将分配到 {nodes} 个节点执行")
        
        # 使用线程池模拟分布式执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=nodes) as executor:
            futures = []
            for node_id in node_ids:
                # 在每个"节点"上运行测试套件的副本
                futures.append(executor.submit(self._run_on_node, node_id))
            
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
        print(f"分布式测试执行完成. 总测试数: {summary['total']}, "
              f"通过: {summary['passed']}, 失败: {summary['failed']}, "
              f"通过率: {summary['pass_rate'] * 100:.2f}%")
              
        return self.merged_results
    
    def _run_on_node(self, node_id: str) -> TestResult:
        """在单个节点上执行测试套件
        
        这是一个内部方法，模拟在远程节点上执行测试
        在实际的分布式环境中，这里应该是与远程节点通信的代码
        """
        print(f"节点 {node_id} 开始执行测试...")
        
        # 创建测试套件的副本
        node_suite = TestSuite(f"{self.test_suite.name}-{node_id}")
        node_suite.test_cases = self.test_suite.test_cases.copy()
        
        # 触发节点开始事件
        for plugin in self.plugins:
            plugin.on_node_start(node_id, node_suite)
        
        # 执行测试
        result = node_suite.run(node_id)
        
        # 触发节点完成事件
        for plugin in self.plugins:
            plugin.on_node_complete(node_id, result)
        
        print(f"节点 {node_id} 测试执行完成.")
        return result 