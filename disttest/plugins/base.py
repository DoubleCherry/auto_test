"""
PluginBase类 - 插件基类
定义插件接口和生命周期事件
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..core import TestSuite, TestResult
    from ..runner import TestRunner


class PluginBase(ABC):
    """插件基类，所有插件必须继承此类并实现相关方法"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.enabled = True
        self.runner = None
        self.metadata: Dict[str, Any] = {}
    
    def setup(self, runner: 'TestRunner') -> None:
        """初始化插件，并与测试运行器关联
        
        Args:
            runner: 测试运行器实例
        """
        self.runner = runner
        self.on_setup()
    
    def on_setup(self) -> None:
        """插件初始化时的额外操作，子类可覆盖此方法"""
        pass
    
    def on_test_run_start(self, test_suite: 'TestSuite') -> None:
        """测试运行开始时的处理
        
        Args:
            test_suite: 将要执行的测试套件
        """
        pass
    
    def on_test_run_complete(self, result: 'TestResult') -> None:
        """测试运行完成时的处理
        
        Args:
            result: 测试结果
        """
        pass
    
    def on_test_progress_update(self, current_result: 'TestResult') -> None:
        """测试进度更新时的处理
        
        Args:
            current_result: 当前的测试结果
        """
        pass
    
    def on_node_start(self, node_id: str, node_suite: 'TestSuite') -> None:
        """节点开始执行测试时的处理
        
        Args:
            node_id: 节点ID
            node_suite: 节点上将要执行的测试套件
        """
        pass
    
    def on_node_complete(self, node_id: str, result: 'TestResult') -> None:
        """节点完成测试时的处理
        
        Args:
            node_id: 节点ID
            result: 节点的测试结果
        """
        pass
    
    def on_error(self, error_message: str, context: Dict[str, Any] = None) -> None:
        """错误发生时的处理
        
        Args:
            error_message: 错误消息
            context: 错误上下文信息
        """
        pass
    
    def cleanup(self) -> None:
        """插件清理操作，在测试运行结束后调用"""
        pass 