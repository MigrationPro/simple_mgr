from typing import List

from cart import Cart
from schemas.product import Product

"""
connector query
POST http://source.com/mp_connector/connector.php?token=0D0D3A92286CBC3D6A87C15F1A144F62&action=query&cart=prestashop
{"query": base64({
    "product": {
            "type": "select",
            "query": "select * from ps_product limit 0,2"
    },
    "product_attribute": {
            "type":"select",
            "query":"select * from ps_product_attribute limit 0,2"
        }
    })
}
"""


class PrestashopExporter:
    def __init__(self, source_data: List[Product], cart: Cart) -> None:
        self.source_data = source_data
        self.cart = cart

    def start(self) -> int:
        migrated_entities_count = 0

        # implement the exporter logic here

        return migrated_entities_count


def get_exporter(source_data: list, cart: Cart):
    return PrestashopExporter(source_data=source_data, cart=cart)
