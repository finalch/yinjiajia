"""
示例：如何添加新的物流公司

要添加新的物流公司，需要：
1. 在 services/logistics/ 下创建新的目录，如 yt/ (圆通)
2. 实现 BaseLogisticsClient 接口
3. 在 LogisticsFactory 中注册新的客户端
"""

from ..base_logistics_client import BaseLogisticsClient, LogisticsOrder, LogisticsResponse


class YtLogisticsClient(BaseLogisticsClient):
    """圆通物流客户端示例"""
    
    def __init__(self, company_name: str = 'yt'):
        super().__init__(company_name)
        # 初始化圆通API配置
        # self.config = YtConfig()
    
    def create_order(self, order: LogisticsOrder) -> LogisticsResponse:
        """创建圆通物流订单"""
        try:
            # 验证订单数据
            if not self.validate_order(order):
                return LogisticsResponse(
                    success=False,
                    error_message="订单数据验证失败"
                )
            
            # TODO: 实现圆通API调用逻辑
            # 1. 构建圆通API请求数据
            # 2. 调用圆通API
            # 3. 解析响应数据
            
            # 示例返回
            return LogisticsResponse(
                success=True,
                shipping_no="YT123456789",
                tracking_number=order.tracking_number,
                logistics_ext_info='{"status": "success"}'
            )
            
        except Exception as e:
            return LogisticsResponse(
                success=False,
                error_message=f"创建圆通订单异常: {str(e)}"
            )
    
    def query_order(self, tracking_number: str) -> LogisticsResponse:
        """查询圆通物流订单状态"""
        # TODO: 实现圆通订单查询接口
        return LogisticsResponse(
            success=False,
            error_message="圆通订单查询功能暂未实现"
        )
    
    def cancel_order(self, tracking_number: str) -> LogisticsResponse:
        """取消圆通物流订单"""
        # TODO: 实现圆通订单取消接口
        return LogisticsResponse(
            success=False,
            error_message="圆通订单取消功能暂未实现"
        )


# 在 LogisticsFactory 中注册新客户端
# LogisticsFactory.register_client('yt', YtLogisticsClient)
