"""
京东物流API客户端
"""
import json
import hashlib
import hmac
import time
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import requests
from config.jd_cfg import JdConfigBase


class JdClient:
    """京东物流API客户端"""
    
    def __init__(self, config: JdConfigBase):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'YinJiaJia-Logistics/1.0'
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成京东API签名"""
        # 按参数名排序
        sorted_params = sorted(params.items())
        # 构建签名字符串
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&secret={self.config.app_secret}"
        
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.config.app_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature
    
    def _build_request_params(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """构建请求参数"""
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4()).replace('-', '')
        
        params = {
            'method': method,
            'app_key': self.config.app_key,
            'timestamp': timestamp,
            'format': 'json',
            'v': '2.0',
            'nonce': nonce,
            'biz_content': json.dumps(data, ensure_ascii=False)
        }
        
        # 生成签名
        params['sign'] = self._generate_signature(params)
        
        return params
    
    def request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        try:
            # 构建请求参数
            params = self._build_request_params(method, data)
            
            # 发送请求
            response = self.session.post(
                self.config.base_url,
                data=params,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'HTTP请求失败: {str(e)}'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'响应解析失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'请求异常: {str(e)}'
            }
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建物流订单"""
        method = 'jingdong.ecap.v1.orders.create'
        return self.request(method, order_data)
    
    def query_order(self, waybill_no: str) -> Dict[str, Any]:
        """查询物流订单"""
        method = 'jingdong.ecap.v1.orders.query'
        data = {'waybillNo': waybill_no}
        return self.request(method, data)
    
    def cancel_order(self, waybill_no: str) -> Dict[str, Any]:
        """取消物流订单"""
        method = 'jingdong.ecap.v1.orders.cancel'
        data = {'waybillNo': waybill_no}
        return self.request(method, data)

