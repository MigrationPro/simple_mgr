import logging
import sys
import requests
import json

from bs4 import BeautifulSoup

from decimal import Decimal

from constants import SpecificPriceType
from typing import List
from cart import Cart
from product import (
    Product, 
    Image, 
    Stock,
    Barcode,
    Weight,
    Variant,
    WeightUnit,
    ManufacturerEntity,
    CategoryInfo,
    SpecificPrice
)


def find_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_request(cart: Cart) -> List:

    url = f"{cart.url}/admin/api/2023-07/products.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": f"{cart.token}"
    }

    response = requests.get(url=url, headers=headers)

    return json.loads(response.text)


def parse_html(html):
    soup = BeautifulSoup(html)
    return soup.get_text()

def parse_product(product: Product) -> Product:

    variants_data = product.get("variants", [])


    product = Product(id=str(product.get("id")),
                    name=product.get("title"),
                    description=parse_html(product.get("body_html")),
                    short_description=None,
                    shop_id=None,
                    lang_id=None,
                    meta_title=product.get("title"),
                    meta_description=parse_html(product.get("body_html")),
                    link_rewrite=product.get("handle", None),
                    price=0,
                    cost=0,
                    is_active=True if product.get("status", False) == "active" else False,
                    is_virtual=None,
                    images=set_images(product),
                    sku=product.get("sku", None),
                    variants=set_variants(variants_data, product),
                    manufacturers=set_manufacturers(product.get("vendor", "").split(",")),
                    categories=set_categories(set_variants(variants_data, product)),
                    specific_prices=set_spesific_prices(set_variants(variants_data, product)),
                    tags=product.get("tags", "").split(","),
                    is_taxable=bool(product.get("taxable", None)) if product.get("taxable", None) else False,
                    stock=set_stocks(None),
                    created_date=product.get("created_at"),
                    updated_date=product.get("updated_at"),         
                    weight=set_weight(product.get("weight") if product.get("weight", None) else None),
                    barcode=set_barcode(None)
                )
    
    return product

def set_manufacturers(manifactures):
    manifactures = [ManufacturerEntity(
        id=None,
        name=man,
        lang_id=None,
        description=None,
        short_description=None,
        meta_title=None,
        meta_description=None,
        created_date=None,
        updated_date=None,
        is_active=None

    ) for man in manifactures if man != " " or man != ""]
    return manifactures

def set_variants(variants_data, product):
    variants = [Variant(id=str(variant_data.get("id")),
                        price=Decimal(variant_data.get("price")),
                        stock=set_stocks(variant_data),
                        sku=variant_data.get("sku"),
                        images=set_images(product),
                        barcode=set_barcode(variant_data),
                        specific_prices=set_spesific_prices(variants_data),
                        attribute_pairs=[],
                        weight=set_weight(variant_data)) for variant_data in variants_data]
    return variants

def set_stocks(variant_data=None):
    if variant_data:
        stock = Stock(quantity=variant_data.get("inventory_quantity"), 
                    out_of_stock_action=variant_data.get("old_inventory_quantity"))
    else:
        stock = Stock(quantity=None, out_of_stock_action=None)
    return stock

def set_categories(variants_data):
    categories = [CategoryInfo(id="",name="",lang_id="") for i in variants_data]
    return categories

def set_weight(variant_data):
    if variant_data:
        weight = Weight(value=Decimal(variant_data.get("weight", 0.0)) + Decimal(variant_data.get("grams", 0.0))/1000, 
                        weight_unit=variant_data.get("weight_unit", WeightUnit.KG))
    else:
        weight = None
    return weight

def set_spesific_prices(variants_data):
    spesific_prices = [
        SpecificPrice(
            id=None,
            country_id="",
            customer_group_id="",
            from_quantity="",
            customer_id="",
            amount_reduction=0,
            percent_reduction="",
            reduction_type=SpecificPriceType.AMOUNT.value,
            start_date=None,
            end_date=None
        )
        for i in variants_data]
    return spesific_prices

def set_barcode(variant_data=None):
    if variant_data:
        barcode = Barcode(ean_13=variant_data.get("barcode"), 
                        upc=variant_data.get("barcode"))
    else:
        barcode = Barcode(ean_13=None, upc=None)
    return barcode

def set_images(product):
    images = [Image(
        id=image_data.get("id", None),
        name=image_data.get("alt", None),
        position=image_data.get("position", None),
        path=image_data.get("src"),
        base64_attachment="",
        is_cover=False
    ) for image_data in product.get("images", [])]

    if product.get("image", None):
        images.append(
            Image(
                id=product.get("image").get("id", None),
                name=product.get("image").get("alt", None),
                position=product.get("image").get("position", None),
                path=product.get("image").get("src"),
                base64_attachment="",
                is_cover=True
            )
        )
    return images
