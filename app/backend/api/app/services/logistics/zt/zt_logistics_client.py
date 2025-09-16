import json
from typing import Dict, Any
from ..base_logistics_client import BaseLogisticsClient, LogisticsOrder, LogisticsResponse
from .zt_client import zt_client
from .zt_order_model import OrderInput, SenderInfoInput, ReceiveInfoInput


class ZtLogisticsClient(BaseLogisticsClient):
    """中通物流客户端"""
    
    def __init__(self, company_name: str = 'zt'):
        super().__init__(company_name)
    
    def create_order(self, order: LogisticsOrder) -> LogisticsResponse:
        """创建中通物流订单"""
        try:
            # 验证订单数据
            if not self.validate_order(order):
                return LogisticsResponse(
                    success=False,
                    error_message="订单数据验证失败"
                )
            
            # 构建中通订单数据
            sender_info = SenderInfoInput(
                sender_name=order.sender_name,
                sender_phone=order.sender_phone,
                sender_province=order.sender_province,
                sender_city=order.sender_city,
                sender_district=order.sender_district,
                sender_address=order.sender_address
            )
            
            receiver_info = ReceiveInfoInput(
                receiver_name=order.receiver_name,
                receiver_phone=order.receiver_phone,
                receiver_province=order.receiver_province,
                receiver_city=order.receiver_city,
                receiver_district=order.receiver_district,
                receiver_address=order.receiver_address
            )
            
            # 创建中通订单
            zt_order = OrderInput(
                sender_info=sender_info,
                receive_info=receiver_info,
                partner_order_code=order.tracking_number
            )
            
            # 调用中通API
            response = zt_client.create_order(zt_order)
            
            if not response:
                return LogisticsResponse(
                    success=False,
                    error_message="创建中通运单失败"
                )
            
            # 解析响应数据
            if isinstance(response, str):
                response_data = json.loads(response)
            else:
                response_data = response
            
            if response_data.get("status"):
                result = response_data.get("result")
                if isinstance(result, str):
                    result = json.loads(result)
                
                return LogisticsResponse(
                    success=True,
                    shipping_no=result.get("billCode"),
                    tracking_number=order.tracking_number,
                    logistics_ext_info=json.dumps(result)
                )
            else:
                return LogisticsResponse(
                    success=False,
                    error_message=response_data.get("message", "创建订单失败")
                )
                
        except Exception as e:
            return LogisticsResponse(
                success=False,
                error_message=f"创建中通订单异常: {str(e)}"
            )
    
    def query_order(self, tracking_number: str) -> LogisticsResponse:
        """查询中通物流订单状态"""
        # TODO: 实现中通订单查询接口
        return LogisticsResponse(
            success=False,
            error_message="中通订单查询功能暂未实现"
        )
    
    def cancel_order(self, tracking_number: str) -> LogisticsResponse:
        """取消中通物流订单"""
        # TODO: 实现中通订单取消接口
        return LogisticsResponse(
            success=False,
            error_message="中通订单取消功能暂未实现"
        )
