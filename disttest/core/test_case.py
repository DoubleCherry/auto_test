"""
TestCase类 - 测试用例基类
支持类级和函数级测试用例
"""
import inspect
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .test_result import TestResult


class TestCase:
    """测试用例基类，所有测试用例都应继承此类"""
    
    def __init__(self):
        self.results = TestResult()
        self._setup_called = False
        self._teardown_called = False
    
    def setup(self) -> None:
        """测试前置处理，在执行测试方法前调用"""
        self._setup_called = True
    
    def teardown(self) -> None:
        """测试后置处理，在执行测试方法后调用"""
        self._teardown_called = True
    
    def setup_class(cls) -> None:
        """类级别的测试前置处理，在执行任何测试方法前调用一次"""
        pass
    
    def teardown_class(cls) -> None:
        """类级别的测试后置处理，在执行所有测试方法后调用一次"""
        pass
    
    def assert_equal(self, actual: Any, expected: Any, message: str = "") -> None:
        """断言两个值相等"""
        if actual != expected:
            msg = message or f"断言失败: {actual} != {expected}"
            raise AssertionError(msg)
    
    def assert_true(self, condition: bool, message: str = "") -> None:
        """断言条件为真"""
        if not condition:
            msg = message or "断言失败: 条件为假"
            raise AssertionError(msg)
    
    def assert_false(self, condition: bool, message: str = "") -> None:
        """断言条件为假"""
        if condition:
            msg = message or "断言失败: 条件为真"
            raise AssertionError(msg)
    
    def assert_raises(self, exception_type: Type[Exception], callable_obj: Callable, *args, **kwargs) -> None:
        """断言调用函数会抛出指定类型的异常"""
        try:
            callable_obj(*args, **kwargs)
        except exception_type:
            return
        except Exception as e:
            raise AssertionError(f"断言失败: 抛出了不同类型的异常: {type(e).__name__}")
        else:
            raise AssertionError(f"断言失败: 没有抛出预期的异常: {exception_type.__name__}")
    
    @classmethod
    def get_test_methods(cls) -> List[str]:
        """获取类中所有的测试方法"""
        return [
            name for name, method in inspect.getmembers(cls, predicate=inspect.isfunction)
            if name.startswith("test_")
        ]
    
    def run_test_method(self, method_name: str) -> Tuple[bool, Optional[str], float]:
        """运行单个测试方法"""
        method = getattr(self, method_name)
        start_time = time.time()
        try:
            self.setup()
            method()
            end_time = time.time()
            self.teardown()
            return True, None, end_time - start_time
        except Exception as e:
            end_time = time.time()
            error_traceback = traceback.format_exc()
            self.teardown()
            return False, f"{type(e).__name__}: {str(e)}\n{error_traceback}", end_time - start_time 