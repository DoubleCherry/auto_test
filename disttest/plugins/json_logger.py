"""
JSONLoggerPlugin - JSON日志插件
用于生成JSON格式的测试日志
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

from .base import PluginBase
from ..core import TestSuite, TestResult


class JSONLoggerPlugin(PluginBase):
    """JSON日志插件，记录测试执行过程和结果"""
    
    def __init__(self, log_dir: str = "logs", log_name: str = None):
        super().__init__()
        self.log_dir = log_dir
        self.log_name = log_name or f"test_log_{int(time.time())}.json"
        self.log_data = {
            "test_run": {
                "start_time": None,
                "end_time": None,
                "summary": {},
            },
            "nodes": {},
            "test_results": []
        }
    
    def on_setup(self) -> None:
        """插件初始化设置"""
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def on_test_run_start(self, test_suite: TestSuite) -> None:
        """测试开始时的处理"""
        start_time = datetime.now()
        self.log_data["test_run"]["start_time"] = start_time.isoformat()
        self.log_data["test_run"]["name"] = test_suite.name
        self.log_data["test_run"]["test_count"] = test_suite.get_total_test_count()
        
        # 写入初始日志
        self._write_log()
    
    def on_test_run_complete(self, result: TestResult) -> None:
        """测试完成时的处理"""
        end_time = datetime.now()
        self.log_data["test_run"]["end_time"] = end_time.isoformat()
        self.log_data["test_run"]["summary"] = result.get_summary()
        
        # 记录所有测试结果
        for test_result in result.results:
            self.log_data["test_results"].append({
                "method_name": test_result.method_name,
                "success": test_result.success,
                "error_message": test_result.error_message,
                "execution_time": test_result.execution_time,
                "start_time": test_result.start_time.isoformat(),
                "additional_data": test_result.additional_data
            })
        
        # 写入最终日志
        self._write_log()
        
        log_path = os.path.join(self.log_dir, self.log_name)
        print(f"JSON测试日志已生成: {os.path.abspath(log_path)}")
    
    def on_test_progress_update(self, current_result: TestResult) -> None:
        """测试进度更新时的处理"""
        # 更新摘要信息
        self.log_data["test_run"]["summary"] = current_result.get_summary()
        
        # 每次进度更新时写入日志，确保实时性
        self._write_log()
    
    def on_node_start(self, node_id: str, node_suite: TestSuite) -> None:
        """节点开始执行时的处理"""
        self.log_data["nodes"][node_id] = {
            "start_time": datetime.now().isoformat(),
            "test_count": node_suite.get_total_test_count(),
            "status": "运行中",
            "end_time": None,
            "summary": None
        }
        
        # 写入日志
        self._write_log()
    
    def on_node_complete(self, node_id: str, result: TestResult) -> None:
        """节点完成测试时的处理"""
        if node_id in self.log_data["nodes"]:
            self.log_data["nodes"][node_id]["end_time"] = datetime.now().isoformat()
            self.log_data["nodes"][node_id]["status"] = "已完成"
            self.log_data["nodes"][node_id]["summary"] = result.get_summary()
            
            # 写入日志
            self._write_log()
    
    def on_error(self, error_message: str, context: Dict[str, Any] = None) -> None:
        """错误发生时的处理"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": error_message,
            "context": context or {}
        }
        
        if "errors" not in self.log_data:
            self.log_data["errors"] = []
            
        self.log_data["errors"].append(error_entry)
        
        # 写入日志
        self._write_log()
    
    def _write_log(self) -> None:
        """写入日志文件"""
        log_path = os.path.join(self.log_dir, self.log_name)
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入日志文件失败: {str(e)}")
    
    def cleanup(self) -> None:
        """插件清理操作"""
        # 确保最后一次写入日志
        self._write_log() 