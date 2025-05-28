"""
NodeManager类 - 节点管理器
用于管理分布式测试节点
"""
import socket
import time
import uuid
from typing import Dict, List, Optional, Any


class Node:
    """测试节点"""
    
    def __init__(self, node_id: str, host: str = "localhost"):
        self.node_id = node_id
        self.host = host
        self.status = "初始化"
        self.last_heartbeat = time.time()
        self.metadata: Dict[str, Any] = {}
    
    def update_heartbeat(self) -> None:
        """更新节点心跳时间"""
        self.last_heartbeat = time.time()
    
    def is_alive(self, timeout: float = 30.0) -> bool:
        """检查节点是否存活"""
        return (time.time() - self.last_heartbeat) < timeout


class NodeManager:
    """节点管理器，用于管理分布式测试节点"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.master_node_id = f"master-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
    
    def register_node(self, host: str = "localhost") -> str:
        """注册新节点"""
        node_id = f"worker-{host}-{uuid.uuid4().hex[:8]}"
        self.nodes[node_id] = Node(node_id, host)
        return node_id
    
    def unregister_node(self, node_id: str) -> None:
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点信息"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[Node]:
        """获取所有节点信息"""
        return list(self.nodes.values())
    
    def get_alive_nodes(self, timeout: float = 30.0) -> List[Node]:
        """获取所有存活的节点"""
        return [node for node in self.nodes.values() if node.is_alive(timeout)]
    
    def update_node_status(self, node_id: str, status: str) -> None:
        """更新节点状态"""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].update_heartbeat()
    
    def wait_for_nodes(self, count: int, timeout: float = 60.0) -> bool:
        """等待指定数量的节点注册
        
        Args:
            count: 期望的节点数量
            timeout: 超时时间（秒）
            
        Returns:
            是否在超时时间内达到期望的节点数量
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if len(self.get_alive_nodes()) >= count:
                return True
            time.sleep(1)
        return False 