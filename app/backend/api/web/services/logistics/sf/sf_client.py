import requests
import json
import time
from typing import Dict, Any, Optional
from config.sf_cfg import sfConfig
from .sf_order import SfOrder

class SfClient:
    """SF快递API统一客户端"""
    
    def __init__(self):
        self.config = sfConfig
        self._access_token = None
        self._token_expires_at = 0
        self._session = requests.Session()
        self._session.headers.update(self.config.headers)
    
    def _get_access_token(self) -> str:
        """获取访问token，优先从内存读取，不存在则通过接口获取"""
        current_time = time.time()
        
        # 检查内存中的token是否有效
        if (self._access_token and 
            self._token_expires_at > current_time):
            return self._access_token
        
        # 通过接口获取新token
        token_data = self._fetch_access_token()
        self._access_token = token_data.get('accessToken')
        # 设置token过期时间（提前5分钟过期，避免边界问题）
        expires_in = token_data.get('expiresIn', 7200)  # 默认2小时
        self._token_expires_at = current_time + expires_in - 300
        
        return self._access_token
    
    def _fetch_access_token(self) -> Dict[str, Any]:
        """调用SF OAuth2接口获取访问token"""
        payload = {
            "grantType": self.config.grant_type,
            "partnerID": self.config.partner_id,
            "secret": self.config.secret
        }
        
        try:
            response = self._session.post(
                self.config.token_url,
                data=payload,  # 使用data而不是json，因为Content-Type是x-www-form-urlencoded
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取SF访问token失败: {str(e)}")
    
    def _update_auth_header(self):
        """更新请求头中的认证信息"""
        token = self._get_access_token()
        self._session.headers.update({
            "Authorization": f"Bearer {token}"
        })
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST请求（用于非SF API的请求）"""
        return self.request("POST", url, data, **kwargs)
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求（用于非SF API的请求）"""
        return self.request("GET", url, **kwargs)
    
    def call_api(self, api_code: str, msg_data: str) -> Dict[str, Any]:
        """调用SF API接口"""
        if api_code not in self.config.code_maps:
            raise ValueError(f"不支持的API接口: {api_code}")
        
        import uuid
        import json
        
        # 构建通用参数
        common_params = {
            "partnerID": self.config.partner_id,
            "requestID": str(uuid.uuid4()),  # 生成唯一请求ID
            "timestamp": str(int(time.time())),  # 当前时间戳
            "serviceCode": self.config.code_maps[api_code],
            "accessToken": self._get_access_token()
        }

        # 将msgData转换为JSON字符串
        common_params["msgData"] = msg_data
        
        # 发送请求到SF API，使用form-data格式
        response = self._session.post(
            self.config.base_url,
            data=common_params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def create_order(self, order_data: SfOrder) -> Dict[str, Any]:
        """创建快递订单"""
        json_data = json.dumps(order_data.to_dict(), ensure_ascii=False)
        return self.call_api("EXP_RECE_CREATE_ORDER", json_data)
    
    def clear_token(self):
        """清除内存中的token（用于测试或重新认证）"""
        self._access_token = None
        self._token_expires_at = 0


# 全局SF客户端实例
sf_client = SfClient()
