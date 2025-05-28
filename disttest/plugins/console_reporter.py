"""
ConsoleReporterPlugin - 控制台测试报告插件
用于在控制台实时显示测试进度和结果
"""
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

from colorama import Fore, Style, init

from .base import PluginBase
from ..core import TestSuite, TestResult

# 初始化colorama
init()


class ConsoleReporterPlugin(PluginBase):
    """控制台测试报告插件，在控制台实时显示测试进度和结果"""
    
    def __init__(self, show_progress: bool = True, verbose: bool = False):
        super().__init__()
        self.show_progress = show_progress
        self.verbose = verbose
        self.start_time = None
        self.active_nodes: Dict[str, Dict[str, Any]] = {}
        self.total_tests = 0
        self.completed_tests = 0
        
    def on_setup(self) -> None:
        """插件初始化设置"""
        pass
    
    def on_test_run_start(self, test_suite: TestSuite) -> None:
        """测试开始时的处理"""
        self.start_time = time.time()
        self.total_tests = test_suite.get_total_test_count()
        
        print(f"\n{Fore.CYAN}==========================================")
        print(f"    开始执行测试: {test_suite.name}")
        print(f"    测试用例数量: {self.total_tests}")
        print(f"    开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"=========================================={Style.RESET_ALL}\n")
    
    def on_test_progress_update(self, current_result: TestResult) -> None:
        """测试进度更新时的处理"""
        if not self.show_progress:
            return
            
        summary = current_result.get_summary()
        self.completed_tests = summary["total"]
        
        # 计算进度百分比
        if self.total_tests > 0:
            progress = min(100, int((self.completed_tests / self.total_tests) * 100))
        else:
            progress = 0
            
        # 创建进度条
        bar_width = 50
        filled_width = int(bar_width * progress / 100)
        bar = '█' * filled_width + '░' * (bar_width - filled_width)
        
        # 清除当前行并显示进度
        sys.stdout.write('\r')
        sys.stdout.write(
            f"{Fore.GREEN}执行进度: [{bar}] {progress}% "
            f"({self.completed_tests}/{self.total_tests}) "
            f"通过: {summary['passed']} 失败: {summary['failed']}{Style.RESET_ALL}"
        )
        sys.stdout.flush()
    
    def on_test_run_complete(self, result: TestResult) -> None:
        """测试完成时的处理"""
        # 如果显示了进度条，先换行
        if self.show_progress:
            print("\n")
            
        # 计算总执行时间
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        summary = result.get_summary()
        
        # 显示结果摘要
        print(f"\n{Fore.CYAN}==========================================")
        print(f"    测试执行完成")
        print(f"    总执行时间: {execution_time:.2f} 秒")
        print(f"    总测试数: {summary['total']}")
        print(f"    通过: {Fore.GREEN}{summary['passed']}{Fore.CYAN}")
        print(f"    失败: {Fore.RED}{summary['failed']}{Fore.CYAN}")
        print(f"    通过率: {Fore.YELLOW}{summary['pass_rate'] * 100:.2f}%{Fore.CYAN}")
        print(f"=========================================={Style.RESET_ALL}\n")
        
        # 如果有失败的测试用例且处于详细模式，显示失败详情
        if summary['failed'] > 0 and self.verbose:
            print(f"{Fore.RED}失败的测试用例:{Style.RESET_ALL}")
            
            for method_result in result.results:
                if not method_result.success:
                    print(f"\n{Fore.RED}测试: {method_result.method_name}")
                    print(f"执行时间: {method_result.execution_time:.3f} 秒")
                    print(f"错误信息: \n{method_result.error_message}{Style.RESET_ALL}")
                    print("-" * 80)
    
    def on_node_start(self, node_id: str, node_suite: TestSuite) -> None:
        """节点开始执行时的处理"""
        self.active_nodes[node_id] = {
            "start_time": time.time(),
            "test_count": node_suite.get_total_test_count()
        }
        
        if self.verbose:
            print(f"{Fore.CYAN}节点 {node_id} 开始执行 {node_suite.get_total_test_count()} 个测试...{Style.RESET_ALL}")
    
    def on_node_complete(self, node_id: str, result: TestResult) -> None:
        """节点完成测试时的处理"""
        if node_id in self.active_nodes:
            start_time = self.active_nodes[node_id]["start_time"]
            end_time = time.time()
            node_execution_time = end_time - start_time
            
            summary = result.get_summary()
            
            if self.verbose:
                print(f"\n{Fore.CYAN}节点 {node_id} 完成执行:")
                print(f"  执行时间: {node_execution_time:.2f} 秒")
                print(f"  测试数: {summary['total']}")
                print(f"  通过: {Fore.GREEN}{summary['passed']}{Fore.CYAN}")
                print(f"  失败: {Fore.RED}{summary['failed']}{Fore.CYAN}")
                print(f"  通过率: {Fore.YELLOW}{summary['pass_rate'] * 100:.2f}%{Fore.CYAN}{Style.RESET_ALL}")
                
            # 从活动节点列表中移除
            del self.active_nodes[node_id] 