import os


class JdConfigBase:
    def __init__(self):
        # self.app_key = "8e028ea4817f4adebe0867447a6675a0"
        # self.app_secret = "07d07121f426408ab23282cc6280fb16"
        # self.access_token = "7c4022da749743ffb24a611c5c44b4c7"
        # self.refresh_token = "77584e5666d64bbda6999e88b1634a67"
        # self.customer_code = "010K11168644"
        self.app_key = "62d07644754843cc882fca7c01476c4f"
        self.app_secret = "0c2c8b6b7c10481ea639f6daa09ac02e"
        self.access_token = "78c246c0ab564e67add6296a9eaf04a1"
        self.customer_code = "27K1234912"
        self.base_url = "https://api.jd.com/routerjson"
        self.paths = {
            "create_order": "/ecap/v1/orders/create",
            "trace_order": "/ecap/v1/orders/trace/query",
            "query_order": "/ecap/v1/orders/query",
            "get_order_status": "/ecap/v1/orders/status/get",
        }


class JdConfigSandbox(JdConfigBase):
    def __init__(self):
        super().__init__()
        # self.base_url = "http://uat-api.jdl.com"
        self.base_url = "https://test-api.jdl.com"


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
