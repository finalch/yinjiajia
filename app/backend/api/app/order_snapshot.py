from models import Product, ProductSpecCombination, Address, User


class UserSnapshot:
    def __init__(self, user: User, address: Address):
        self.user = {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "email": user.email
        }
        self.address = {
            "id": address.id,
            "user_id": address.user_id,
            "receiver_name": address.receiver_name,
            "phone": address.phone,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "is_default": address.is_default,
            "detail_address": address.detail_address
        }


class ProductItemSnapshot:
    def __init__(self, product: Product, spec: ProductSpecCombination):
        self.product = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "status": product.status
        }
        self.spec = {
            "id": spec.id,
            "product_id": spec.product_id,
            "price": spec.price,
            "stock": spec.stock,
            "status": spec.status
        }
