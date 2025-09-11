from typing import Dict


class ProductSpec:
    def __init__(self, spec_id, price, spec: Dict):
        self.spec_id = spec_id
        self.price = price
        self.spec = spec


class ProductSnapshot:
    def __init__(self, product_id, name, price, specs: ProductSpec):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.specs = specs
