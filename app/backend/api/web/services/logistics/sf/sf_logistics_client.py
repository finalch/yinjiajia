import json

from .sf_client import sf_client
from .sf_order import SfOrder, CargoDetail, ContactInfo
from ..base_logistics_client import BaseLogisticsClient, LogisticsOrder, LogisticsResponse, LogisticsRoute


class SfLogisticsClient(BaseLogisticsClient):
    """顺丰物流客户端"""

    def __init__(self, company_name: str = 'sf'):
        super().__init__(company_name)

    def create_order(self, order: LogisticsOrder) -> LogisticsResponse:
        """创建顺丰物流订单"""
        try:
            # 验证订单数据
            if not self.validate_order(order):
                return LogisticsResponse(
                    success=False,
                    error_message="订单数据验证失败"
                )

            # 构建顺丰订单数据
            cargo_details = []
            for cargo in order.cargo_details:
                cargo_details.append(CargoDetail(cargo.get('name', '-')))

            # 构建联系人信息
            sender_contact = ContactInfo(
                contact_type=1,
                name=order.sender_name,
                phone=order.sender_phone,
                country='CN',
                province=order.sender_province,
                city=order.sender_city,
                address=order.sender_address
            )

            receiver_contact = ContactInfo(
                contact_type=2,
                name=order.receiver_name,
                phone=order.receiver_phone,
                country='CN',
                province=order.receiver_province,
                city=order.receiver_city,
                address=order.receiver_address
            )

            # 创建顺丰订单
            sf_order = SfOrder(
                order_id=order.tracking_number,
                cargo_details=cargo_details,
                contact_info_List=[sender_contact, receiver_contact]
            )

            # 调用顺丰API
            response = sf_client.create_order(sf_order)

            if not response or not response.get("apiResultData"):
                return LogisticsResponse(
                    success=False,
                    error_message="创建顺丰运单失败"
                )

            # 解析响应数据
            logistics_ext_info = response.get("apiResultData")
            result_data = json.loads(logistics_ext_info)

            if result_data.get('success'):
                shipping_no = result_data['msgData']['waybillNoInfoList'][0]['waybillNo']
                return LogisticsResponse(
                    success=True,
                    shipping_no=shipping_no,
                    tracking_number=order.tracking_number,
                    logistics_ext_info=logistics_ext_info
                )
            else:
                return LogisticsResponse(
                    success=False,
                    error_message=result_data.get('errorMsg', '创建订单失败')
                )

        except Exception as e:
            return LogisticsResponse(
                success=False,
                error_message=f"创建顺丰订单异常: {str(e)}"
            )

    def query_order(self, shipping_no: str) -> LogisticsResponse:
        """查询顺丰物流订单状态"""
        # TODO: 实现顺丰订单查询接口
        response = sf_client.query_order(shipping_no)
        if not response or not response.get("apiResultCode") or response.get("apiResultCode") != "A1000":
            raise Exception("查询顺丰运单失败")
        else:
            strs = response.get("apiResultData")
            routes_info = json.loads(strs)
            routes = routes_info['msgData']['routeResps'][0]['routes']
            logistics_route = [
                LogisticsRoute(
                    time=route['acceptTime'],
                    address=route['acceptAddress'],
                    remark=route['remark'],
                    opCode=route['opCode'],
                    firstStatusCode=route.get('firstStatusCode'),
                    firstStatusName=route.get('firstStatusName'),
                    secondaryStatusCode=route.get('secondaryStatusCode'),
                    secondaryStatusName=route.get('secondaryStatusName')
                )
                for route in routes
            ]
            return logistics_route

    def cancel_order(self, tracking_number: str) -> LogisticsResponse:
        """取消顺丰物流订单"""
        # TODO: 实现顺丰订单取消接口
        return LogisticsResponse(
            success=False,
            error_message="顺丰订单取消功能暂未实现"
        )
