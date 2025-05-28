"""
HTMLReportPlugin - HTML测试报告生成插件
"""
import os
import time
from datetime import datetime
from typing import Dict, Any, List

import jinja2

from .base import PluginBase
from ..core import TestResult


class HTMLReportPlugin(PluginBase):
    """HTML测试报告生成插件"""
    
    def __init__(self, output_dir: str = "reports", report_name: str = None):
        super().__init__()
        self.output_dir = output_dir
        self.report_name = report_name or f"test_report_{int(time.time())}.html"
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.template_name = "report_template.html"
        self.results: List[Dict[str, Any]] = []
        
    def on_setup(self) -> None:
        """插件初始化设置"""
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 如果模板目录不存在，创建一个基本模板
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            self._create_default_template()
    
    def on_test_run_complete(self, result: TestResult) -> None:
        """测试运行完成时生成HTML报告"""
        report_data = self._prepare_report_data(result)
        self._generate_report(report_data)
        
        report_path = os.path.join(self.output_dir, self.report_name)
        print(f"HTML测试报告已生成: {os.path.abspath(report_path)}")
    
    def on_node_complete(self, node_id: str, result: TestResult) -> None:
        """节点完成测试时记录结果"""
        summary = result.get_summary()
        summary["node_id"] = node_id
        self.results.append(summary)
    
    def _prepare_report_data(self, result: TestResult) -> Dict[str, Any]:
        """准备报告数据"""
        summary = result.get_summary()
        
        # 收集失败的测试用例详情
        failed_tests = []
        for method_result in result.results:
            if not method_result.success:
                failed_tests.append({
                    "test_name": method_result.method_name,
                    "error_message": method_result.error_message,
                    "execution_time": method_result.execution_time
                })
        
        # 计算节点统计信息
        nodes_summary = {}
        for node_result in self.results:
            node_id = node_result["node_id"]
            nodes_summary[node_id] = {
                "total": node_result["total"],
                "passed": node_result["passed"],
                "failed": node_result["failed"],
                "pass_rate": node_result["pass_rate"] * 100
            }
        
        return {
            "title": "分布式测试执行报告",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": summary["total_time"],
            "summary": {
                "total": summary["total"],
                "passed": summary["passed"],
                "failed": summary["failed"],
                "pass_rate": summary["pass_rate"] * 100
            },
            "nodes": nodes_summary,
            "failed_tests": failed_tests
        }
    
    def _generate_report(self, report_data: Dict[str, Any]) -> None:
        """生成HTML报告"""
        template_loader = jinja2.FileSystemLoader(searchpath=self.template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(self.template_name)
        
        output = template.render(**report_data)
        
        report_path = os.path.join(self.output_dir, self.report_name)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(output)
    
    def _create_default_template(self) -> None:
        """创建默认的HTML报告模板"""
        template_path = os.path.join(self.template_dir, self.template_name)
        
        template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .summary {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
        }
        .summary-box {
            text-align: center;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            flex: 1;
            margin: 0 10px;
        }
        .pass {
            background-color: #dff0d8;
            border: 1px solid #d6e9c6;
        }
        .fail {
            background-color: #f2dede;
            border: 1px solid #ebccd1;
        }
        .total {
            background-color: #d9edf7;
            border: 1px solid #bce8f1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        .node-results {
            margin-bottom: 30px;
        }
        .failed-tests {
            margin-bottom: 30px;
        }
        .error-message {
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>生成时间: {{ timestamp }}</p>
        <p>总执行时间: {{ "%.2f"|format(duration) }} 秒</p>
    </div>
    
    <div class="summary">
        <div class="summary-box total">
            <h2>总计</h2>
            <h3>{{ summary.total }}</h3>
        </div>
        <div class="summary-box pass">
            <h2>通过</h2>
            <h3>{{ summary.passed }}</h3>
        </div>
        <div class="summary-box fail">
            <h2>失败</h2>
            <h3>{{ summary.failed }}</h3>
        </div>
        <div class="summary-box total">
            <h2>通过率</h2>
            <h3>{{ "%.2f"|format(summary.pass_rate) }}%</h3>
        </div>
    </div>
    
    <div class="node-results">
        <h2>节点执行情况</h2>
        <table>
            <tr>
                <th>节点ID</th>
                <th>总计</th>
                <th>通过</th>
                <th>失败</th>
                <th>通过率</th>
            </tr>
            {% for node_id, node_data in nodes.items() %}
            <tr>
                <td>{{ node_id }}</td>
                <td>{{ node_data.total }}</td>
                <td>{{ node_data.passed }}</td>
                <td>{{ node_data.failed }}</td>
                <td>{{ "%.2f"|format(node_data.pass_rate) }}%</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    {% if failed_tests %}
    <div class="failed-tests">
        <h2>失败的测试用例</h2>
        <table>
            <tr>
                <th>测试名称</th>
                <th>执行时间 (秒)</th>
                <th>错误信息</th>
            </tr>
            {% for test in failed_tests %}
            <tr>
                <td>{{ test.test_name }}</td>
                <td>{{ "%.3f"|format(test.execution_time) }}</td>
                <td><div class="error-message">{{ test.error_message }}</div></td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% else %}
    <div class="passed-message">
        <h2>恭喜！所有测试用例均通过。</h2>
    </div>
    {% endif %}
</body>
</html>"""
        
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content) 