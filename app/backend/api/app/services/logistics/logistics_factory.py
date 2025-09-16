from typing import Dict, Type
from .base_logistics_client import BaseLogisticsClient
from .sf.sf_logistics_client import SfLogisticsClient
from .zt.zt_logistics_client import ZtLogisticsClient
from .jd.jd_logistics_client import JdLogisticsClient


class LogisticsFactory:
    """物流服务工厂类"""
    
    _clients: Dict[str, Type[BaseLogisticsClient]] = {
        'sf': SfLogisticsClient,
        'zt': ZtLogisticsClient,
        'jd': JdLogisticsClient,
    }
    
    @classmethod
    def create_client(cls, company: str) -> BaseLogisticsClient:
        """根据公司名称创建对应的物流客户端"""
        company = company.lower()
        
        if company not in cls._clients:
            raise ValueError(f"不支持的物流公司: {company}")
        
        client_class = cls._clients[company]
        return client_class(company)
    
    @classmethod
    def register_client(cls, company: str, client_class: Type[BaseLogisticsClient]):
        """注册新的物流客户端"""
        cls._clients[company.lower()] = client_class
    
    @classmethod
    def get_supported_companies(cls) -> list:
        """获取支持的物流公司列表"""
        return list(cls._clients.keys())
    
    @classmethod
    def is_supported(cls, company: str) -> bool:
        """检查是否支持指定的物流公司"""
        return company.lower() in cls._clients
