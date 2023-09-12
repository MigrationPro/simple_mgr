from typing import List

from cart import Cart
from product import Product, Image, Variant, Barcode, Weight, Stock
from utils import get_products


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        products: List[Product] = []
        response = get_products(self.cart.url, self.cart.token)
        for p in response["products"]:
            product = Product(
                id=p["id"],
                name=p["title"],
                description=p["body_html"],
                short_description=p["body_html"],
                meta_title=p["title"],
                meta_description=p["body_html"],
                shop_id=None,  # TODO
                lang_id=None,  # TODO
                link_rewrite=None,  # TODO
                price=p["variants"][0]["price"],
                cost=p["variants"][0]["price"],  # TODO
                is_active=True if p["status"] == "active" else False,
                is_virtual=False,  # TODO
                is_taxable=p["variants"][0]["taxable"],
                sku=p["variants"][0]["sku"],
                created_date=p["created_at"],
                updated_date=p["updated_at"],
                images=[
                    Image(
                        id=image["id"],
                        name=image["alt"],
                        position=image["position"],
                        path=image["src"],
                        base64_attachment=None,
                        is_cover=True if image["id"] == p["image"]["id"] else False,
                    ) for image in p["images"]
                ],
                variants=[
                    Variant(
                        id=variant["id"],
                        price=variant["price"],
                        stock=variant["inventory_quantity"],
                        sku=variant["sku"],
                        specific_prices=[],  # TODO
                        images=[],  # TODO
                        attribute_pairs=[],  # TODO
                        barcode=Barcode(ean_13=variant["barcode"], upc=None),
                        weight=Weight(value=variant["weight"]),
                    ) for variant in p["variants"]
                ],
                manufacturers=[],  # TODO
                categories=[],  # TODO
                specific_prices=[],  # TODO
                tags=p["tags"].split(","),
                stock=Stock(
                    quantity=p["variants"][0]["inventory_quantity"],
                    out_of_stock_action="deny_backorders" if p["variants"][0]["inventory_policy"] == "deny" else "allow_backorders",
                ),
                weight=Weight(
                    value=p["variants"][0]["weight"]
                ),
                barcode=Barcode(ean_13=p["variants"][0]["barcode"], upc=None),
            )
            products.append(product)

        return products


def get_importer(cart):
    return ShopifyImporter(cart)
