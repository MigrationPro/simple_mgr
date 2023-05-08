
import requests
from typing import List

from cart import Cart
from product import *
from typing import Dict, Any, List
from decimal import Decimal


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        products: List[Product] = []

        # implement the importer logic here
        url = f"{self.cart.url}/admin/api/2023-04/products.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.cart.token
        }

        response = requests.get(url, headers=headers)


        if response.status_code == 200:
            data = response.json()

            for product in data["products"]:
                tags = product.get('tags', '').split(',')
              
                images = [Image(
                    id=image_data["id"],
                    name=image_data.get("name", None),
                    position=image_data["position"],
                    path=image_data["src"],
                    base64_attachment=None,
                    is_cover=False if image_data["position"] != 1 else True,
                ) for image_data in product.get('images', [])]
                  
                attribute_groups = [AttributeGroup(        
                    id=option["id"],
                    name=option["name"],
                    position=option["position"],
                    lang_id=None,
                    attributes={attr: Attribute(id=None, name=attr, position=None, lang_id=None) for attr in option["values"]}
                    )
                    for option in product.get('options', [])
                ]

                attribute_pairs = [AttributePair(attribute=attr, attribute_group=attr_group)
                   for attr_group in attribute_groups
                   for attr in attr_group.attributes.values()]
                
                def calcute_specific_price(variant:dict) -> dict:
                    amount_reduction = percent_reduction = reduction_type = None
                    compare_at_price = variant["compare_at_price"]

                    if compare_at_price:
                        amount_reduction = Decimal(compare_at_price) - Decimal(variant["price"])
                        percent_reduction = amount_reduction / Decimal(compare_at_price) * 100
                        reduction_type = SpecificPriceType.AMOUNT

                    specific_price = SpecificPrice(
                        id=None,
                        country_id=None,
                        customer_id=None,
                        customer_group_id=None,
                        from_quantity=None,
                        amount_reduction=amount_reduction,
                        percent_reduction=percent_reduction,
                        reduction_type=reduction_type,
                        start_date=None,
                        end_date=None,
                    )
                    
                    return specific_price

                def create_stock(variant: dict) -> dict:
                    stock = Stock(
                        quantity=int(variant.get('inventory_quantity', 0)), 
                        out_of_stock_action=int(variant.get('out_of_stock_action', 0))
                        )
                    return stock
               
                def create_weight(variant: dict) -> dict:
                    weight=Weight(
                        value=Decimal(variant["weight"]),
                        weight_unit=variant["weight_unit"]),
                    return weight
               
                variants = [Variant(
                    id = variant["id"], 
                    price=Decimal(variant["price"]), 
                    stock = create_stock(variant), 
                    sku=variant["sku"],
                    barcode=Barcode(
                        ean_13=variant["barcode"],
                        upc=None),
                    weight=create_weight(variant),
                    specific_prices = [calcute_specific_price(variant)],
                    images=[img for img in images if img.id == variant["image_id"]],
                    attribute_pairs=attribute_pairs
                    ) for variant in product.get('variants', [])]

                new_product = Product(
                    id=str(product.get('id')), 
                    name=product.get('title', None), 
                    description=product.get('body_html', None), 
                    short_description = product.get('short_description', None),
                    shop_id = product.get('shop_id', None),
                    lang_id = product.get('lang_id', None),
                    meta_title = product.get('meta_title', None),
                    meta_description = product.get('meta_description', None),
                    price=Decimal(product['variants'][0].get('price', 0)), 
                    is_active=product.get('status', None) == 'active',
                    cost=Decimal(product['variants'][0].get('cost', Decimal(0))),
                    is_virtual=product.get('is_virtual', False),
                    images=images,
                    sku=product['variants'][0].get('sku', None),
                    variants=variants,
                    manufacturers=None,
                    categories=None,
                    specific_prices=variants[0].specific_prices,
                    tags=tags,
                    is_taxable=product.get('is_taxable', True),
                    stock = sum(variant.stock.quantity for variant in variants),
                    link_rewrite=product.get('link_rewrite', None),
                    created_date=product.get('created_at', None),
                    updated_date=product.get('updated_at', None),
                    weight=variants[0].weight,
                    barcode=variants[0].barcode
                )
                products.append(new_product)
 
        return products


def get_importer(cart):
    return ShopifyImporter(cart)