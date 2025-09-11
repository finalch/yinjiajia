import os
class JdConfigBase:
    def __init__(self):
        self.app_key = "8e028ea4817f4adebe0867447a6675a0"
        self.app_secret = "07d07121f426408ab23282cc6280fb16"
        self.base_url = "https://api.jd.com/routerjson"
        self.paths = {
            "create_order": "/ecap/v1/orders/create"
        }

class JdConfigSandbox(JdConfigBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://uat-api.jdl.com"

class JdConfigProduction(JdConfigBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.jdl.com"


def get_jd_config():
    """根据环境变量获取对应的配置"""
    env = os.getenv("ENV", "sandbox").lower()
    
    if env == "production":
        return JdConfigProduction()
    else:
        return JdConfigSandbox()


# 默认配置实例（沙盒环境）
jdConfig = get_jd_config()