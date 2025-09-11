import os


class ZTConfigBase:
    """ZT快递API基础配置类"""

    def __init__(self):
        self.x_app_key = "e58e4863617b4e2c4b0c8"
        self.x_app_secret = "d89f5124df78603b1190095ecbd85562"
        # 请求头配置
        self.headers = {
            "Content-Type": "application/json"
        }


class ZTConfigSandbox(ZTConfigBase):
    """ZT快递API沙盒环境配置"""

    def __init__(self):
        super().__init__()
        self.x_app_key = "e58e4863617b4e2c4b0c8"
        self.x_app_secret = "d89f5124df78603b1190095ecbd85562"
        self.base_url = "https://japi-test.zto.com/"


class ZTConfigProduction(ZTConfigBase):
    """ZT快递API生产环境配置"""

    def __init__(self):
        super().__init__()
        self.x_app_key = "e58e4863617b4e2c4b0c8"
        self.x_app_secret = "d89f5124df78603b1190095ecbd85562"
        self.base_url = "https://japi.zto.com/"


def get_config():
    """根据环境变量获取对应的ZT配置"""
    env = os.getenv("ENV", "sandbox").lower()

    if env == "production":
        return ZTConfigProduction()
    else:
        return ZTConfigSandbox()


# 默认配置实例（沙盒环境）
sfConfig = get_config()
