class SenderInfoInput:
    def __init__(self, sender_name: str,
                 sender_phone: str,
                 sender_province: str,
                 sender_city: str,
                 sender_district: str,
                 sender_address: str):
        self.senderName = sender_name
        self.senderPhone = sender_phone
        self.senderProvince = sender_province
        self.senderCity = sender_city
        self.senderDistrict = sender_district
        self.senderAddress = sender_address


class ReceiveInfoInput:
    def __init__(self, receiver_name: str,
                 receiver_phone: str,
                 receiver_province: str,
                 receiver_city: str,
                 receiver_district: str,
                 receiver_address: str):
        self.receiverName = receiver_name
        self.receiverPhone = receiver_phone
        self.receiverProvince = receiver_province
        self.receiverCity = receiver_city
        self.receiverDistrict = receiver_district
        self.receiverAddress = receiver_address


class OrderInput:
    def __init__(self,
                 sender_info: SenderInfoInput,
                 receive_info: ReceiveInfoInput,
                 partner_order_code: str):
        self.partnerType = 2
        self.orderType = 1
        self.partnerOrderCode = partner_order_code
        self.senderInfo = sender_info
        self.receiveInfo = receive_info

    def to_dict(self):
        return {
            "partnerType": self.partnerType,
            "orderType": self.orderType,
            "partnerOrderCode": self.partnerOrderCode,
            "senderInfo": self.senderInfo.__dict__,
            "receiveInfo": self.receiveInfo.__dict__
        }
