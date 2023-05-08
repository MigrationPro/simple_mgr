from typing import List

import requests

from cart import Cart
from parsers.product import ProductParser
from schemas.product import Product
from utils import find_logger

logger = find_logger(__name__)


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        # implement the importer logic here
        products = self.get_products()

        return products

    def get_products(self) -> List[Product]:
        api_version = "2023-04"
        url = f"{self.cart.url}/admin/api/{api_version}/products.json"
        headers = {
            "X-Shopify-Access-Token": self.cart.token,
            "Content-Type": "application/json",
        }
        response = requests.get(url=url, headers=headers)
        body = response.json()
        logger.info(f"Response status code: {response.status_code}")

        products_raw = body.get("products", [])
        products: List[Product] = []

        for product_raw in products_raw:
            product = ProductParser(product_raw).parse()
            products.append(product)
            logger.debug(f"Product: {product}")
            break

        return products


def get_importer(cart):
    return ShopifyImporter(cart)
