"""
京东物流客户端实现
"""
import json
from typing import Dict, Any

from config.jd_cfg import jdConfig
from config.log import get_logger

from .jd_client import JdClient
from .jd_order_model import JdOrderRequest, JdSenderInfo, JdReceiverInfo, JdCargoDetail
from ..base_logistics_client import BaseLogisticsClient, LogisticsOrder, LogisticsResponse, LogisticsRoute

logger = get_logger(__name__)


class JdLogisticsClient(BaseLogisticsClient):
    """京东物流客户端"""

    def __init__(self, company_name: str = 'jd'):
        super().__init__(company_name)

        self.client = JdClient(jdConfig)

    def create_order(self, order: LogisticsOrder) -> LogisticsResponse:
        """创建京东物流订单"""
        try:
            # 验证订单数据
            if not self.validate_order(order):
                return LogisticsResponse(
                    success=False,
                    error_message="订单数据验证失败"
                )

            # 构建京东API请求数据
            jd_request = self._build_jd_order_request(order)

            # 调用京东API
            response = self.client.create_order(jd_request.to_dict())

            # 解析响应
            return self._parse_create_response(response, order.tracking_number)

        except Exception as e:
            logger.error(f"创建京东物流订单异常: {str(e)}")
            return LogisticsResponse(
                success=False,
                error_message=f"创建京东物流订单异常: {str(e)}"
            )

    def query_order(self, tracking_number: str) -> LogisticsResponse:
        """查询京东物流订单状态"""
        try:
            # 从跟踪号中提取运单号
            waybill_no = self._extract_waybill_no(tracking_number)
            if not waybill_no:
                return LogisticsResponse(
                    success=False,
                    error_message="无效的跟踪号"
                )

            # 调用京东API查询
            response = self.client.trace_order(waybill_no)

            # 解析响应
            return self._parse_query_response(response, tracking_number)

        except Exception as e:
            logger.error(f"查询京东物流订单异常: {str(e)}")
            return LogisticsResponse(
                success=False,
                error_message=f"查询京东物流订单异常: {str(e)}"
            )

    def cancel_order(self, tracking_number: str) -> LogisticsResponse:
        """取消京东物流订单"""
        try:
            # 从跟踪号中提取运单号
            waybill_no = self._extract_waybill_no(tracking_number)
            if not waybill_no:
                return LogisticsResponse(
                    success=False,
                    error_message="无效的跟踪号"
                )

            # 调用京东API取消
            response = self.client.cancel_order(waybill_no)

            # 解析响应
            return self._parse_cancel_response(response, tracking_number)

        except Exception as e:
            logger.error(f"取消京东物流订单异常: {str(e)}")
            return LogisticsResponse(
                success=False,
                error_message=f"取消京东物流订单异常: {str(e)}"
            )

    def _build_jd_order_request(self, order: LogisticsOrder) -> JdOrderRequest:
        """构建京东订单请求"""
        # 构建寄件人信息
        sender = JdSenderInfo(
            name=order.sender_name,
            phone=order.sender_phone,
            province=order.sender_province,
            city=order.sender_city,
            district=order.sender_district,
            address=order.sender_city + order.sender_district + order.sender_address
        )

        # 构建收件人信息
        receiver = JdReceiverInfo(
            name=order.receiver_name,
            phone=order.receiver_phone,
            province=order.receiver_province,
            city=order.receiver_city,
            district=order.receiver_district,
            address=order.receiver_province + order.receiver_city + order.receiver_district + order.receiver_address
        )

        # 构建货物详情
        cargo_details = []
        for cargo in order.cargo_details:
            cargo_detail = JdCargoDetail(
                name=cargo.get('name', '商品'),
                weight=cargo.get('weight', 1.0),
                value=cargo.get('value', 0.0),
                quantity=cargo.get('quantity', 1)
            )
            cargo_details.append(cargo_detail)

        # 构建京东订单请求
        jd_request = JdOrderRequest(
            order_id=order.tracking_number,
            service_type="STANDARD_EXPRESS",
            sender=sender,
            receiver=receiver,
            cargo_details=cargo_details,
            remark=f"订单号: {order.order_id}"
        )

        return jd_request

    def _parse_create_response(self, response: Dict[str, Any], tracking_number: str) -> LogisticsResponse:
        """解析创建订单响应"""
        try:
            if response.get('success', False):
                # 提取运单号
                result_data = response.get('data', {})
                waybill_no = result_data.get('waybillCode')

                if waybill_no:
                    return LogisticsResponse(
                        success=True,
                        shipping_no=waybill_no,
                        tracking_number=tracking_number,
                        logistics_ext_info=json.dumps(response, ensure_ascii=False)
                    )
                else:
                    return LogisticsResponse(
                        success=False,
                        error_message="响应中未找到运单号"
                    )
            else:
                error_msg = response.get('error', '未知错误')
                return LogisticsResponse(
                    success=False,
                    error_message=f"京东API错误: {error_msg}"
                )

        except Exception as e:
            return LogisticsResponse(
                success=False,
                error_message=f"解析响应失败: {str(e)}"
            )

    def _parse_query_response(self, response: Dict[str, Any], tracking_number: str) -> list[LogisticsRoute]:
        """解析查询订单响应"""
        try:
            if response.get('success', False):
                result_data = response.get('data', {}).get('traceDetails', [])
                logistics_routes = [
                    LogisticsRoute(
                        time=item.get('operationTime', ''),
                        remark=item.get('operationTitle', ''),
                        opCode=item.get('operationCode', ''),
                        firstStatusCode=item.get('firstStatusCode', ''),
                        firstStatusName=item.get('firstStatusName', ''),
                        secondaryStatusCode=item.get('secondaryStatusCode', ''),
                        secondaryStatusName=item.get('secondaryStatusName', ''),
                        address=item.get('operationAddress', '')
                    ) for item in result_data
                ]
                return logistics_routes
            else:
                raise Exception("查询失败")
        except Exception as e:
            print(e)
            raise Exception("解析查询响应失败")

    def _parse_cancel_response(self, response: Dict[str, Any], tracking_number: str) -> LogisticsResponse:
        """解析取消订单响应"""
        try:
            if response.get('success', False):
                return LogisticsResponse(
                    success=True,
                    tracking_number=tracking_number,
                    logistics_ext_info=json.dumps(response, ensure_ascii=False)
                )
            else:
                error_msg = response.get('error', '取消失败')
                return LogisticsResponse(
                    success=False,
                    error_message=f"取消失败: {error_msg}"
                )

        except Exception as e:
            return LogisticsResponse(
                success=False,
                error_message=f"解析取消响应失败: {str(e)}"
            )

    def _extract_waybill_no(self, tracking_number: str) -> str:
        """从跟踪号中提取运单号"""
        # 京东跟踪号格式: JD-{waybill_no}
        if tracking_number.startswith('JD-'):
            return tracking_number[3:]
        return tracking_number
