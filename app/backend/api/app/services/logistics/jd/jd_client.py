"""
京东物流API客户端
"""
import hashlib
import json
import time
from typing import Dict, Any

import requests
from config.jd_cfg import JdConfigBase


class JdClient:
    """京东物流API客户端"""

    def __init__(self, config: JdConfigBase):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _generate_signature(self, params: bytes) -> str:
        """生成京东API签名"""
        # 按参数名排序
        # sorted_params = sorted(params.items())
        # # 构建签名字符串
        # sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        # sign_str += f"&secret={self.config.app_secret}"
        #
        # # 使用HMAC-SHA256生成签名
        # signature = hmac.new(
        #     self.config.app_secret.encode('utf-8'),
        #     sign_str.encode('utf-8'),
        #     hashlib.sha256
        # ).hexdigest().upper()
        h = hashlib.md5()
        h.update(params)
        return h.digest().hex()

    def _build_request_params(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """构建请求参数"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # timestamp = "2025-09-20 00:25:55"
        params_json = json.dumps(data, ensure_ascii=False, sort_keys=False)
        content = "".join([
            self.config.app_secret,
            "access_token", self.config.access_token,
            "app_key", self.config.app_key,
            "method", method,
            "param_json", params_json,
            "timestamp", timestamp,
            "v", "2.0",
            self.config.app_secret
        ])
        # 生成签名
        sign = self._generate_signature(content.encode("UTF-8"))
        params = {
            'app_key': self.config.app_key,
            'access_token': self.config.access_token,
            'sign': sign,
            'timestamp': timestamp,
            'LOP-DN': 'ECAP',
            'v': '2.0',
            'algorithm': 'md5-salt'
        }
        return params

    def request(self, url: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        try:
            # 构建请求参数
            json_data = [data]
            params = self._build_request_params(method, json_data)

            # 发送请求
            response = self.session.post(
                url=url,
                params=params,
                data=json.dumps(json_data, ensure_ascii=False, sort_keys=False).encode("UTF-8"),
                timeout=30,
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'Connection': 'close',
                    'Accept-Encoding': 'identity'
                }
            )
            response.raise_for_status()
            result = response.json()

            # url = url + "?" + urlencode(queries)
            # body = json.dumps(json_data, ensure_ascii=False, sort_keys=False)
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            # opener = urllib.request.build_opener()
            # http_request = urllib.request.Request(url=url, data=body.encode("UTF-8"), headers=headers)
            # http_response = opener.open(http_request)
            # print(http_response.status)
            # print(http_response.headers)
            # print(http_response.read().decode("UTF-8"))
            #
            print(result)
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
        method = self.config.paths['create_order']
        url = self.config.base_url + method
        order_data['customer_code'] = self.config.customer_code
        return self.request(url, method, order_data)

    def query_order(self, waybill_no: str) -> Dict[str, Any]:
        """查询物流订单"""
        method = self.config.paths['query_order']
        url = self.config.base_url + method
        data = {'orderOrigin': 1, 'waybillCode': waybill_no, 'customerCode': self.config.customer_code}
        return self.request(url, method, data)

    def trace_order(self, waybill_no: str) -> Dict[str, Any]:
        method = self.config.paths['trace_order']
        url = self.config.base_url + method
        data = {'orderOrigin': 1, 'waybillCode': waybill_no, 'customerCode': self.config.customer_code}
        return self.request(url, method, data)

    def get_order_status(self, waybill_no: str) -> str:
        method = self.config.paths['get_order_status']
        url = self.config.base_url + method
        data = {'orderOrigin': 1, 'waybillCode': waybill_no, 'customerCode': self.config.customer_code}
        return self.request(url, method, data)

    def cancel_order(self, waybill_no: str) -> Dict[str, Any]:
        """取消物流订单"""
        method = 'jingdong.ecap.v1.orders.cancel'
        data = {'waybillNo': waybill_no}
        return self.request(method, data)
