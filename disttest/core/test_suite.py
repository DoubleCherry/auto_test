"""
TestSuite类 - 测试套件管理
用于管理多个测试用例的集合
"""
import inspect
from typing import Dict, List, Type, Optional, Any

from .test_case import TestCase
from .test_result import TestResult, TestMethodResult


class TestSuite:
    """测试套件，用于组织和管理多个测试用例"""
    
    def __init__(self, name: str = "默认测试套件"):
        self.name = name
        self.test_cases: List[Type[TestCase]] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_test_case(self, test_case_class: Type[TestCase]) -> None:
        """添加测试用例类到套件中"""
        if not inspect.isclass(test_case_class) or not issubclass(test_case_class, TestCase):
            raise TypeError(f"测试用例必须是TestCase的子类: {test_case_class}")
        
        self.test_cases.append(test_case_class)
    
    def add_test_cases(self, test_case_classes: List[Type[TestCase]]) -> None:
        """批量添加多个测试用例类"""
        for test_case_class in test_case_classes:
            self.add_test_case(test_case_class)
    
    def run(self, node_id: str = "local") -> TestResult:
        """执行测试套件中的所有测试用例"""
        merged_result = TestResult()
        merged_result.test_case_name = self.name
        merged_result.node_id = node_id
        
        for test_case_class in self.test_cases:
            # 调用类级别的setup
            if hasattr(test_case_class, 'setup_class'):
                test_case_class.setup_class()
            
            test_instance = test_case_class()
            test_methods = test_case_class.get_test_methods()
            
            # 创建这个测试用例的结果
            test_case_result = TestResult()
            test_case_result.test_case_name = test_case_class.__name__
            test_case_result.node_id = node_id
            
            for method_name in test_methods:
                success, error, execution_time = test_instance.run_test_method(method_name)
                
                # 收集测试用例的结果
                for method_result in test_instance.results.results:
                    test_case_result.add_result(method_result)
            
            # 合并这个测试用例的结果到总结果中
            merged_result.merge(test_case_result)
            
            # 调用类级别的teardown
            if hasattr(test_case_class, 'teardown_class'):
                test_case_class.teardown_class()
        
        merged_result.set_complete()
        return merged_result
    
    def get_total_test_count(self) -> int:
        """获取测试套件中测试方法的总数"""
        return len(self.test_cases)
    
    def get_total_method_count(self) -> int:
        """获取测试套件中所有测试方法的总数"""
        total = 0
        for test_case_class in self.test_cases:
            total += len(test_case_class.get_test_methods())
        return total 