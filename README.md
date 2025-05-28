# 分布式自动化测试框架 (DistTest)

一个基于Python的分布式自动化测试框架，支持模块化测试用例管理、多节点并行执行、实时结果汇总以及插件扩展。

## 主要特性

1. **模块化测试管理**：支持类级和函数级测试用例编写
2. **分布式执行**：利用Python并发库实现多节点并行测试
3. **实时结果汇总**：所有节点的测试结果实时汇总到主控节点
4. **插件扩展系统**：支持自定义报告生成、日志处理等插件

## 安装方法

```bash
pip install -r requirements.txt
```

## 使用示例

```python
# 创建测试用例
from disttest.core import TestCase

class MyTest(TestCase):
    def test_example(self):
        self.assert_equal(1 + 1, 2)
        
# 运行测试
from disttest.runner import TestRunner

runner = TestRunner()
runner.add_test_case(MyTest)
runner.run_distributed(nodes=3)
```

## 插件使用

```python
from disttest.plugins import HTMLReportPlugin

runner = TestRunner()
runner.add_plugin(HTMLReportPlugin(output_dir="reports"))
runner.run_distributed(nodes=3)
``` 