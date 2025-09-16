"""
京东物流订单数据模型
"""
from typing import List, Optional, Dict, Any


class JdSenderInfo:
    """寄件人信息"""
    name: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    post_code: Optional[str] = None


class JdReceiverInfo:
    """收件人信息"""
    name: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    post_code: Optional[str] = None


class JdCargoDetail:
    """货物详情"""
    name: str
    weight: float  # 重量(kg)
    value: float  # 价值(元)
    quantity: int = 1
    remark: Optional[str] = None


class JdOrderRequest:
    """京东物流订单请求"""
    order_id: str
    service_type: str = "STANDARD_EXPRESS"  # 服务类型
    sender: JdSenderInfo
    receiver: JdReceiverInfo
    cargo_details: List[JdCargoDetail]
    remark: Optional[str] = None
    insurance_value: Optional[float] = None  # 保价金额
    cod_value: Optional[float] = None  # 代收金额

    def to_dict(self) -> Dict[str, Any]:
        """转换为京东API请求格式"""
        return {
            "orderId": self.order_id,
            "serviceType": self.service_type,
            "sender": {
                "name": self.sender.name,
                "phone": self.sender.phone,
                "province": self.sender.province,
                "city": self.sender.city,
                "district": self.sender.district,
                "address": self.sender.address,
                "postCode": self.sender.post_code
            },
            "receiver": {
                "name": self.receiver.name,
                "phone": self.receiver.phone,
                "province": self.receiver.province,
                "city": self.receiver.city,
                "district": self.receiver.district,
                "address": self.receiver.address,
                "postCode": self.receiver.post_code
            },
            "cargoDetails": [
                {
                    "name": cargo.name,
                    "weight": cargo.weight,
                    "value": cargo.value,
                    "quantity": cargo.quantity,
                    "remark": cargo.remark
                }
                for cargo in self.cargo_details
            ],
            "remark": self.remark,
            "insuranceValue": self.insurance_value,
            "codValue": self.cod_value
        }

class JdOrderResponse:
    """京东物流订单响应"""
    success: bool
    order_id: Optional[str] = None
    waybill_no: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
