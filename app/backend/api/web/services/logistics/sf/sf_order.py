class CargoDetail:
    def __init__(self, cargo_name: str):
        self.name = cargo_name


class ContactInfo:
    def __init__(self, contact_type: int, name: str, phone: str, country: str, province: str, city: str, address: str):
        self.contactType = contact_type
        self.contact = name
        self.tel = phone
        self.country = country
        self.province = province
        self.city = city
        self.address = address


class SfOrder:
    def __init__(self, order_id: str, cargo_details: list[CargoDetail], contact_info_List: list[ContactInfo]):
        self.orderId = order_id
        self.language = "zh-CN"
        self.cargoDetails = cargo_details
        self.contactInfoList = contact_info_List
    
    def to_dict(self):
        """转换为可序列化的字典"""
        return {
            'orderId': self.orderId,
            'language': self.language,
            'cargoDetails': [cargo.__dict__ for cargo in self.cargoDetails],
            'contactInfoList': [contact.__dict__ for contact in self.contactInfoList]
        }
