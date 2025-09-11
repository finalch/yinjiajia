"""
京东物流使用示例
"""
from services.logistics.logistics_factory import LogisticsFactory
from services.logistics.base_logistics_client import LogisticsOrder


def example_create_jd_order():
    """示例：创建京东物流订单"""
    
    # 1. 创建京东物流客户端
    jd_client = LogisticsFactory.create_client('jd')
    
    # 2. 构建物流订单数据
    order = LogisticsOrder(
        order_id="ORDER_20241201_001",
        tracking_number="JD-20241201001",
        sender_name="银家家商城",
        sender_phone="400-123-4567",
        sender_province="北京市",
        sender_city="北京市", 
        sender_district="朝阳区",
        sender_address="朝阳区建国路88号SOHO现代城",
        receiver_name="张三",
        receiver_phone="13800138000",
        receiver_province="上海市",
        receiver_city="上海市",
        receiver_district="浦东新区", 
        receiver_address="浦东新区陆家嘴环路1000号",
        cargo_details=[
            {
                "name": "iPhone 15 Pro",
                "weight": 0.5,
                "value": 7999.0,
                "quantity": 1
            },
            {
                "name": "AirPods Pro",
                "weight": 0.2,
                "value": 1899.0,
                "quantity": 1
            }
        ]
    )
    
    # 3. 创建物流订单
    result = jd_client.create_order(order)
    
    if result.success:
        print(f"✓ 京东物流订单创建成功")
        print(f"  运单号: {result.shipping_no}")
        print(f"  跟踪号: {result.tracking_number}")
        return result
    else:
        print(f"✗ 京东物流订单创建失败: {result.error_message}")
        return None


def example_query_jd_order(tracking_number: str):
    """示例：查询京东物流订单"""
    
    # 1. 创建京东物流客户端
    jd_client = LogisticsFactory.create_client('jd')
    
    # 2. 查询订单状态
    result = jd_client.query_order(tracking_number)
    
    if result.success:
        print(f"✓ 查询成功")
        print(f"  运单号: {result.shipping_no}")
        print(f"  跟踪号: {result.tracking_number}")
        print(f"  物流信息: {result.logistics_ext_info}")
        return result
    else:
        print(f"✗ 查询失败: {result.error_message}")
        return None


def example_cancel_jd_order(tracking_number: str):
    """示例：取消京东物流订单"""
    
    # 1. 创建京东物流客户端
    jd_client = LogisticsFactory.create_client('jd')
    
    # 2. 取消订单
    result = jd_client.cancel_order(tracking_number)
    
    if result.success:
        print(f"✓ 取消成功")
        print(f"  跟踪号: {result.tracking_number}")
        return result
    else:
        print(f"✗ 取消失败: {result.error_message}")
        return None


def example_in_logistics_api():
    """示例：在物流API中使用京东物流"""
    
    # 模拟物流API中的使用方式
    merchant_id = 1
    order_id = "ORDER_20241201_001"
    company = "jd"  # 使用京东物流
    
    try:
        # 检查是否支持该物流公司
        if not LogisticsFactory.is_supported(company):
            print(f"暂不支持物流公司: {company}")
            return
        
        # 创建物流客户端
        logistics_client = LogisticsFactory.create_client(company)
        
        # 构建物流订单（这里需要从数据库获取订单信息）
        # 实际使用中，这些数据来自数据库查询
        order = LogisticsOrder(
            order_id=order_id,
            tracking_number=logistics_client._create_tracking_number(),
            sender_name="商家名称",
            sender_phone="商家电话",
            sender_province="商家省份",
            sender_city="商家城市",
            sender_district="商家区县",
            sender_address="商家地址",
            receiver_name="收货人姓名",
            receiver_phone="收货人电话",
            receiver_province="收货省份",
            receiver_city="收货城市",
            receiver_district="收货区县",
            receiver_address="收货地址",
            cargo_details=[{"name": "商品名称", "weight": 1.0, "value": 100.0}]
        )
        
        # 创建物流订单
        result = logistics_client.create_order(order)
        
        if result.success:
            print(f"✓ 物流订单创建成功")
            print(f"  运单号: {result.shipping_no}")
            print(f"  跟踪号: {result.tracking_number}")
            
            # 这里可以将结果保存到数据库
            # 更新订单状态为已发货等
            
        else:
            print(f"✗ 物流订单创建失败: {result.error_message}")
            
    except Exception as e:
        print(f"✗ 物流API调用异常: {str(e)}")


if __name__ == "__main__":
    print("=== 京东物流使用示例 ===\n")
    
    # 示例1：创建订单
    print("1. 创建京东物流订单示例")
    result = example_create_jd_order()
    
    if result and result.shipping_no:
        # 示例2：查询订单
        print("\n2. 查询京东物流订单示例")
        example_query_jd_order(result.tracking_number)
        
        # 示例3：取消订单（可选）
        # print("\n3. 取消京东物流订单示例")
        # example_cancel_jd_order(result.tracking_number)
    
    # 示例4：在物流API中使用
    print("\n4. 在物流API中使用京东物流示例")
    example_in_logistics_api()
    
    print("\n=== 示例完成 ===")

