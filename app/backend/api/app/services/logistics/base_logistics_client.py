from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class LogisticsOrder:
    """统一的物流订单数据结构"""
    order_id: str
    tracking_number: str
    sender_name: str
    sender_phone: str
    sender_province: str
    sender_city: str
    sender_district: str
    sender_address: str
    receiver_name: str
    receiver_phone: str
    receiver_province: str
    receiver_city: str
    receiver_district: str
    receiver_address: str
    cargo_details: List[Dict[str, Any]]  # 货物详情列表


@dataclass
class LogisticsResponse:
    """统一的物流响应数据结构"""
    success: bool
    shipping_no: Optional[str] = None
    tracking_number: Optional[str] = None
    logistics_ext_info: Optional[str] = None
    error_message: Optional[str] = None
@dataclass
class LogisticsRoute:
    """物流路由信息"""
    time: str
    address: str
    remark: str
    opCode: str
    firstStatusCode: str
    firstStatusName: str
    secondaryStatusCode: str
    secondaryStatusName: str

@dataclass
class LogisticsRoutes:
    """物流路由信息"""
    route: List[LogisticsRoute]


class BaseLogisticsClient(ABC):
    """物流客户端抽象基类"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
    
    @abstractmethod
    def create_order(self, order: LogisticsOrder) -> LogisticsResponse:
        """创建物流订单"""
        pass
    
    @abstractmethod
    def query_order(self, tracking_number: str) -> LogisticsResponse:
        """查询物流订单状态"""
        pass
    
    @abstractmethod
    def cancel_order(self, tracking_number: str) -> LogisticsResponse:
        """取消物流订单"""
        pass
    
    def validate_order(self, order: LogisticsOrder) -> bool:
        """验证订单数据是否有效"""
        required_fields = [
            order.order_id, order.tracking_number,
            order.sender_name, order.sender_phone,
            order.receiver_name, order.receiver_phone
        ]
        return all(field and str(field).strip() for field in required_fields)
    
    def _create_tracking_number(self) -> str:
        """生成跟踪号"""
        import uuid
        return f"{self.company_name.upper()}-{uuid.uuid4().hex}"
