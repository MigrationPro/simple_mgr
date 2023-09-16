import requests

from typing import List

from cart import Cart
from product import Product
from utils import get_request, parse_product


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        products: List[Product] = []

        raw_product_list = get_request(self.cart).get("products", None)

        products = [parse_product(product) for product in raw_product_list]

        return products

def get_importer(cart):
    return ShopifyImporter(cart)