"""
TestResult类 - 测试结果管理
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set


@dataclass
class TestMethodResult:
    """单个测试方法的结果"""
    method_name: str
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        # 用于去重的哈希方法
        return hash((self.method_name, self.start_time))


class TestResult:
    """测试结果集合，包含多个测试方法的结果"""
    
    def __init__(self):
        self.test_case_name: str = ""
        self.node_id: str = ""
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None
        self.results: List[TestMethodResult] = []
        self.metadata: Dict[str, Any] = {}
        self._method_names: Set[str] = set()  # 用于跟踪已添加的方法名称
    
    def add_result(self, method_result: TestMethodResult) -> None:
        """添加单个方法的测试结果"""
        # 避免重复添加相同的测试方法结果
        if method_result.method_name not in self._method_names:
            self.results.append(method_result)
            self._method_names.add(method_result.method_name)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试结果汇总信息"""
        total = len(self.results)
        passed = sum(1 for result in self.results if result.success)
        failed = total - passed
        
        total_time = sum(result.execution_time for result in self.results)
        
        return {
            "test_case_name": self.test_case_name,
            "node_id": self.node_id,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "total_time": total_time,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
    
    def merge(self, other_result: 'TestResult') -> None:
        """合并另一个测试结果"""
        if not other_result.results:
            return
            
        # 避免重复添加相同的测试方法结果
        for result in other_result.results:
            self.add_result(result)
        
        # 更新结束时间为最晚的结束时间
        if other_result.end_time:
            if not self.end_time or other_result.end_time > self.end_time:
                self.end_time = other_result.end_time
                
        # 合并元数据
        for key, value in other_result.metadata.items():
            if key not in self.metadata:
                self.metadata[key] = value
    
    def set_complete(self) -> None:
        """标记测试结果完成"""
        self.end_time = datetime.now() 