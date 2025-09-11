import json
import os
from typing import Dict, Any

import requests
from config.zt_cfg import get_config

from . import signature
from .zt_order_model import OrderInput


class ZTClient:
    def __init__(self):
        self.config = get_config()
        self._session = requests.Session()

    def request(self,
                method: str,
                url: str,
                data: Any,
                **kwargs) -> Dict[str, Any]:

        # 将数据转换为JSON字符串
        body_str = json.dumps(data, ensure_ascii=False)
        
        # 使用字符串进行签名计算
        s = signature.signature(body_str + self.config.x_app_secret)
        
        # 将字符串编码为UTF-8字节用于发送
        body_bytes = body_str.encode('utf-8')
        
        headers = {
            'x-appKey': self.config.x_app_key,
            'x-dataDigest': s,
            'content-type': 'application/json'
        }
        try:
            response = self._session.request(
                method=method,
                url=url,
                data=body_bytes,
                timeout=30,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.text()  # 修复：使用json()而不是text()
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP请求失败: {str(e)}")

    def create_order(self, data: OrderInput) -> Dict[str, Any]:
        url = os.path.join(self.config.base_url, 'zto.open.createOrder')
        return self.request('POST', url, data.to_dict())


zt_client = ZTClient()
