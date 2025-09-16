import os


class SfConfigBase:
    """SF快递API基础配置类"""

    def __init__(self):
        self.partner_id = "SCLRK8HMXWP4"
        self.secret = "u22DlmnHD5MzlDBf1TjicWMCLlDXY7FK"
        self.grant_type = "password"

        # API接口映射
        self.code_maps = {
            "EXP_RECE_CREATE_ORDER": "EXP_RECE_CREATE_ORDER",  # 下单接口
            "EXP_RECE_SEARCH_ROUTES": "EXP_RECE_SEARCH_ROUTES"
        }

        # 请求头配置
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }


class SfConfigSandbox(SfConfigBase):
    """SF快递API沙盒环境配置"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://sfapi-sbox.sf-express.com/std/service"
        self.token_url = "https://sfapi-sbox.sf-express.com/oauth2/accessToken"


class SfConfigProduction(SfConfigBase):
    """SF快递API生产环境配置"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://bspgw.sf-express.com/std/service"
        self.token_url = "https://sfapi.sf-express.com/oauth2/accessToken"

        # 生产环境特定配置（需要从环境变量或配置文件读取）
        self.partner_id = os.getenv("SF_PARTNER_ID", "your_production_partner_id")
        self.secret = os.getenv("SF_SECRET", "your_production_secret")

        # 更新headers中的partner_id
        self.headers["sf-partner-id"] = self.partner_id


def get_sf_config():
    """根据环境变量获取对应的SF配置"""
    env = os.getenv("ENV", "sandbox").lower()

    if env == "production":
        return SfConfigProduction()
    else:
        return SfConfigSandbox()


# 默认配置实例（沙盒环境）
sfConfig = get_sf_config()
