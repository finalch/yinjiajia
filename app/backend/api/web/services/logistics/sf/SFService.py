import json
import uuid
from datetime import datetime
from typing import List

from flask import jsonify

from app.backend.api.web.config.log import get_logger
from app.backend.api.web.models import Merchant, db, OrderItem
from app.backend.api.web.services.sf_client import sf_client
from app.backend.api.web.services.sf_order import CargoDetail, ContactInfo, SfOrder

logger = get_logger(__name__)


def create(items: List[OrderItem], merchant: Merchant, address: dict):
    tracking_number = 'SF-' + uuid.uuid4().hex
    cargo_details = []
    for item in items:
        # 获取商品信息
        snapshot = item.snapshot
        name = "-"
        if snapshot:
            snapshot = json.loads(snapshot)
            name = snapshot['product']['name']
        cargo_details.append(CargoDetail(name))
    m_contact_info = ContactInfo(1, merchant.name, merchant.phone, 'CN', '北京', '北京市', '朝阳区xxx路xxx小区')
    u_contact_info = ContactInfo(2, address["receiver_name"], address["phone"], 'CN', address["province"], address["city"], address["detail_address"])
    contact_infos = [m_contact_info, u_contact_info]
    sf_order = SfOrder(tracking_number, cargo_details, contact_infos)
    response = sf_client.create_order(sf_order)
    if response and response.get("apiResultData"):
        logistics_ext_info = response.get("apiResultData")
        result_data = json.loads(logistics_ext_info)
    else:
        return jsonify(code=500, message='创建顺丰运单失败'), 500
    if result_data['success']:
        shipping_no = result_data['msgData']['waybillNoInfoList'][0]['waybillNo']
        logger.debug('创建顺丰运单成功, 运单号: {}'.format(shipping_no))
        for item in items:
            item.shipping_no = shipping_no
            item.logistics_ext_info = logistics_ext_info
            item.tracking_number = tracking_number
            item.shipping_company = 'sf'
            item.shipped_at = datetime.utcnow()
            item.item_status = 'shipped'
            db.session.commit()
        return shipping_no
    return None
