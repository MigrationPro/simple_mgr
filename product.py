from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from typing import Dict, List, Optional

from constants import OutOfStock, SpecificPriceType


"""
The data classes can be changed and adapted to the needs of the developer and task
"""
class WeightUnit(Enum):
    KG = 1
    GR = 2


@dataclass
class Weight:
    value: Decimal
    weight_unit: WeightUnit = None


@dataclass
class Attribute:
    id: Optional[str]
    name: str
    position: Optional[str]
    lang_id: Optional[str]


@dataclass
class Stock:
    quantity: Optional[int]
    out_of_stock_action: Optional[OutOfStock]


@dataclass
class AttributeGroup:
    id: Optional[str]
    name: str
    position: int
    lang_id: Optional[str]
    attributes: Dict[str, Attribute]

    def get_attribute_by(self, identifier: str) -> Attribute:
        return self.attributes[identifier]

    def get_identifier(self, identifier_name: str) -> str:
        return getattr(self, identifier_name)


@dataclass
class AttributePair:
    attribute: Attribute
    attribute_group: AttributeGroup


@dataclass
class Image:
    id: Optional[str]
    name: Optional[str]
    position: Optional[str]
    path: str
    base64_attachment: Optional[str]
    is_cover: bool = False


@dataclass
class Barcode:
    upc: Optional[str]
    ean_13: Optional[str]

    @property
    def value(self):
        return self.upc or self.ean_13


@dataclass
class SpecificPrice:
    id: Optional[str]
    country_id: Optional[str]
    customer_group_id: Optional[str]
    customer_id: Optional[str]
    from_quantity: Optional[int]
    amount_reduction: Optional[Decimal]
    percent_reduction: Optional[Decimal]
    reduction_type: SpecificPriceType
    start_date: Optional[datetime]
    end_date: Optional[datetime]


@dataclass
class ManufacturerEntity:
    id: Optional[str]
    name: str
    lang_id: Optional[str]
    description: Optional[str]
    short_description: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    is_active: Optional[bool]


@dataclass
class CategoryInfo:
    id: str
    name: Optional[str]
    lang_id: Optional[str]


@dataclass
class Variant:
    id: str
    price: Decimal
    stock: Stock
    sku: Optional[str]
    specific_prices: List[SpecificPrice]
    images: List[Image]
    attribute_pairs: List[AttributePair]
    barcode: Barcode = Barcode(ean_13=None, upc=None)
    weight: Weight = Weight(value=None)


@dataclass
class Product:
    id: str
    name: str
    description: Optional[str]
    short_description: Optional[str]
    shop_id: Optional[str]
    lang_id: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    link_rewrite: Optional[str]
    price: Decimal
    cost: Decimal
    is_active: bool
    is_virtual: bool
    images: List[Image]
    sku: Optional[str]
    variants: List[Variant]
    manufacturers: List[ManufacturerEntity]
    categories: List[CategoryInfo]
    specific_prices: List[SpecificPrice]
    tags: List[str]
    is_taxable: Optional[bool]
    stock: Stock
    link_rewrite: Optional[str]
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    weight: Weight = Weight(value=None)
    barcode: Barcode = Barcode(ean_13=None, upc=None)

