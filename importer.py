import requests

from typing import List

from cart import Cart
from product import (
    Product,
    Image,
    Variant,
    Barcode,
    Weight,
    Stock,
    ManufacturerEntity,
    SpecificPrice,
    SpecificPriceType,
    AttributePair,
    AttributeGroup,
    Attribute,
    CategoryInfo
)


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        products: List[Product] = []
        response = self.get_products()
        collects = self.get_collects()
        for p in response["products"]:
            product = Product(
                id=p["id"],
                name=p["title"],
                description=p["body_html"],
                short_description=p["body_html"],
                meta_title=p["title"],
                meta_description=p["body_html"],
                shop_id=None,
                lang_id=None,
                link_rewrite=p["handle"],
                price=p["variants"][0]["price"],
                cost=p["variants"][0]["price"],
                is_active=True if p["status"] == "active" else False,
                is_virtual=True if p["published_scope"] == "global" else False,
                is_taxable=p["variants"][0]["taxable"],
                sku=p["variants"][0]["sku"],
                created_date=p["created_at"],
                updated_date=p["updated_at"],
                images=self.get_images(p),
                variants=self.get_variants(p),
                manufacturers=self.get_manufacturers(p),
                categories=self.get_categories(p, collects),
                specific_prices=self.get_specific_prices(p),
                tags=p["tags"].split(","),
                stock=self.get_stock(p),
                weight=Weight(
                    value=p["variants"][0]["weight"]
                ),
                barcode=Barcode(ean_13=p["variants"][0]["barcode"], upc=None),
            )
            products.append(product)

        return products

    def get_products(self):
        url = f"https://{self.cart.url}.myshopify.com/admin/api/2023-07/products.json"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': f'{self.cart.token}'
        }

        response = requests.get(url, headers=headers, data=payload)

        return response.json()

    def get_collects(self):
        url = f"https://{self.cart.url}.myshopify.com/admin/api/2023-07/collects.json"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': f'{self.cart.token}'
        }

        response = requests.get(url, headers=headers, data=payload)
        return response.json()

    def get_collect_by_id(self, collect_id):
        url = f"https://{self.cart.url}.myshopify.com/admin/api/2023-07/collections/{collect_id}.json"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': f'{self.cart.token}'
        }

        response = requests.get(url, headers=headers, data=payload)

        return response.json()

    def get_images(self, product, variant=None):
        images: List[Image] = [
            Image(
                id=image["id"],
                name=image["alt"],
                position=image["position"],
                path=image["src"],
                base64_attachment=None,
                is_cover=True if image["id"] == product["image"]["id"] else False,
            ) for image in product["images"] if variant and image["id"] == variant["image_id"]
        ]
        return images

    def get_variants(self, product):
        variants: List[Variant] = [
            Variant(
                id=variant["id"],
                price=variant["price"],
                stock=variant["inventory_quantity"],
                sku=variant["sku"],
                specific_prices=self.get_specific_prices(product),
                images=self.get_images(product, variant=variant),
                attribute_pairs=self.get_attribute_pairs(product),
                barcode=Barcode(ean_13=variant["barcode"], upc=None),
                weight=Weight(value=variant["weight"]),
            ) for variant in product["variants"]
        ]
        return variants

    def get_manufacturers(self, product):
        manufacturers: List[ManufacturerEntity] = [
            ManufacturerEntity(
                id=product["vendor"],
                name=product["vendor"],
                lang_id=None,
                description=None,
                short_description=None,
                meta_title=None,
                meta_description=None,
                created_date=None,
                updated_date=None,
                is_active=True,
            )]
        return manufacturers

    def get_specific_prices(self, product):
        specific_prices: List[SpecificPrice] = [
            SpecificPrice(
                id=product["variants"][0]["id"],
                country_id=None,
                customer_group_id=None,
                customer_id=None,
                start_date=None,
                end_date=None,
                from_quantity=product["variants"][0]["compare_at_price"],
                amount_reduction=float(
                    product["variants"][0]["compare_at_price"]) - float(product["variants"][0]["price"]),
                percent_reduction=round(((float(product["variants"][0]["compare_at_price"]) - float(
                    product["variants"][0]["price"])) / float(product["variants"][0]["compare_at_price"])) * 100, 2),
                reduction_type=SpecificPriceType.AMOUNT if float(product["variants"][0]["compare_at_price"]) - float(
                    product["variants"][0]["price"]) > 0 else SpecificPriceType.PERCENTAGE,
            )]
        return specific_prices

    def get_attribute_pairs(self, product):
        attribute_pairs: List[AttributePair] = [
            AttributePair(
                attribute=[
                    Attribute(
                        id=option["id"],
                        name=value,
                        position=option["position"],
                        lang_id=None,
                    ) for value in option["values"]
                ],
                attribute_group=AttributeGroup(
                    id=option["id"],
                    name=option["name"],
                    lang_id=None,
                    attributes=[
                        Attribute(
                            id=option["id"],
                            name=value,
                            position=option["position"],
                            lang_id=None,
                        ) for value in option["values"]
                    ],
                ),
            ) for option in product["options"]
        ]
        return attribute_pairs

    def get_categories(self, product, collects):
        categories: List[CategoryInfo] = [
            CategoryInfo(
                id=collect["collection_id"],
                name=self.get_collect_by_id(collect["collection_id"])[
                    "collection"]["title"],
                lang_id=None,
            ) for collect in collects["collects"] if collect["product_id"] == product["id"]
        ]
        return categories

    def get_stock(self, product):
        stocks: List[Stock] = [
            Stock(
                quantity=product["variants"][0]["inventory_quantity"],
                out_of_stock_action="deny_backorders" if product["variants"][0][
                    "inventory_policy"] == "deny" else "allow_backorders",
            ),
        ]
        return stocks


def get_importer(cart):
    return ShopifyImporter(cart)
