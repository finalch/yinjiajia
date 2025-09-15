from typing import Dict

from ..models import Product, OrderItem, ProductSpecCombination, Address, User


class ProductSpec:
    def __init__(self, spec_id, price, spec: Dict):
        self.spec_id = spec_id
        self.price = price
        self.spec = spec


class ProductItemSnapshot:
    def __init__(self, product: Product, spec: ProductSpecCombination, user: User, address: Address):
        self.product = product,
        self.spec = spec,
        self.address = address,
        self.user = user
