from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from constants import SpecificPriceType
from schemas.product import (
    Image,
    AttributeGroup,
    Attribute,
    Product,
    AttributePair,
    WeightUnit,
    Weight,
    Variant,
    Stock,
    SpecificPrice,
)
from utils import find_logger

logger = find_logger(__name__)


class ProductParser:
    """
    This class is responsible for parsing the product data from the source cart to Product dataclass.
    """

    def __init__(self, product: dict) -> None:
        """
        Initializes a ProductParser object.

        Args:
          product: The product data dictionary.
        """

        self.product: dict = product
        self.attribute_groups: List[AttributeGroup] = self.parse_attribute_groups()
        self.images: List[Image] = self.parse_images()
        self.variants: List[Variant] = self.parse_variants()

    def parse(self) -> Product:
        """
        Parses the product data and returns a Product dataclass.

        Returns:
          A Product dataclass.
        """

        default_variant = self.variants[0]
        result = Product(
            id=self.product["id"],
            name=self.product["title"],
            description=self.product["body_html"],
            short_description=None,
            tags=self.parse_tags(),
            images=self.images,
            created_date=datetime.strptime(
                self.product["created_at"], "%Y-%m-%dT%H:%M:%S%z"
            ),
            updated_date=datetime.strptime(
                self.product["created_at"], "%Y-%m-%dT%H:%M:%S%z"
            ),
            is_active=self.product["status"] == "active",
            is_taxable=default_variant.is_taxable,
            is_virtual=default_variant.is_virtual,
            link_rewrite=None,
            lang_id=None,
            meta_title=None,
            meta_description=None,
            price=default_variant.price,
            weight=default_variant.weight,
            barcode=default_variant.barcode,
            variants=self.variants,
            categories=None,
            manufacturers=self.product["vendor"],
            specific_prices=default_variant.specific_prices,
            cost=None,
            sku=default_variant.sku,
            shop_id=None,
            stock=default_variant.stock,
        )
        return result

    def parse_tags(self) -> Optional[List[str]]:
        """
        Parses the tags from the product data and returns a list of strings.

        Returns:
          A list of strings, or None if there are no tags.
        """

        tags_str = self.product.get("tags", None)
        if tags_str:
            tags = tags_str.split(",")
        else:
            tags = None
        return tags

    def parse_attribute_groups(self) -> List[AttributeGroup]:
        """
        Parses the attribute groups from the product data and returns a list of AttributeGroup dataclasses.

        Returns:
          A list of AttributeGroup dataclasses.
        """

        options_raw = self.product.get("options", None)
        attribute_groups: List[AttributeGroup] = []
        for option_raw in options_raw:
            attribute_group = self.parse_attribute_group(option_raw)
            attribute_groups.append(attribute_group)
        return attribute_groups

    def parse_attribute_group(self, option_raw: dict) -> AttributeGroup:
        """
        Parses an attribute group from the product data and returns an AttributeGroup dataclass.

        Args:
          option_raw: The attribute group data dictionary.

        Returns:
          An AttributeGroup dataclass.
        """

        attribute_group = AttributeGroup(
            id=option_raw["id"],
            name=option_raw["name"],
            lang_id=None,
            attributes={},
        )

        attributes_raw = option_raw.get("values", [])
        for attribute_raw in attributes_raw:
            attribute = Attribute(
                id=None,
                name=attribute_raw,
                position=None,
                lang_id=None,
            )
            attribute_group.attributes[attribute.name] = attribute

        return attribute_group

    def parse_images(self) -> List[Image]:
        """
        Parses the images from the product data and returns a list of Image dataclasses.

        Returns:
          A list of Image dataclasses.
        """

        images_raw = self.product["images"]
        images: List[Image] = []
        for image_raw in images_raw:
            image = self.parse_image(image_raw)
            images.append(image)
        return images

    def parse_image(self, image_raw: dict) -> Image:
        """
        Parses an image from the product data and returns an Image dataclass.

        Args:
          image_raw: The image data dictionary.

        Returns:
          An Image dataclass.
        """

        position = image_raw["position"]
        image = Image(
            id=image_raw["id"],
            path=image_raw["src"],
            name=image_raw["alt"],
            position=str(position),
            base64_attachment=None,
        )
        image.is_cover = position == 1

        return image

    def parse_variants(self) -> List[Variant]:
        """
        Parses the variants from the product data and returns a list of Variant dataclasses.

        Returns:
          A list of Variant dataclasses.
        """

        variants_raw = self.product["variants"]
        variants: List[Variant] = []

        for variant_raw in variants_raw:
            variant = self.parse_variant(variant_raw)
            variants.append(variant)

        return variants

    def parse_variant(self, variant_raw: dict) -> Variant:
        """
        Parses a variant from the product data and returns a Variant dataclass.

        Args:
          variant_raw: The variant data dictionary.

        Returns:
          A Variant dataclass.
        """

        price = Decimal(variant_raw["price"])
        images = self.get_variant_images(variant_raw)
        attribute_pairs = self.parse_variant_options(variant_raw)
        specific_prices = self.parse_variant_specific_prices(variant_raw)

        grams = Decimal(variant_raw["grams"])
        weight = Weight(
            value=grams,
            weight_unit=WeightUnit.GR,
        )

        stock = Stock(
            quantity=variant_raw["inventory_quantity"],
            out_of_stock_action=None,
        )

        variant = Variant(
            id=variant_raw["id"],
            sku=variant_raw["sku"],
            barcode=variant_raw["barcode"],
            price=price,
            weight=weight,
            images=images,
            stock=stock,
            is_taxable=bool(variant_raw["taxable"]),
            is_virtual=bool(variant_raw["requires_shipping"]),
            attribute_pairs=attribute_pairs,
            specific_prices=specific_prices,
        )
        return variant

    def parse_variant_options(self, variant_raw: dict) -> List[AttributePair]:
        """
        Parses the variant options from the product data and returns a list of AttributePair dataclasses.

        Args:
          variant_raw: The variant data dictionary.

        Returns:
          A list of AttributePair dataclasses.
        """

        attribute_pairs: List[AttributePair] = []

        variant_options = (
            variant_raw["option1"],
            variant_raw["option2"],
            variant_raw["option3"],
        )
        for i in range(len(variant_options)):
            variant_option = variant_options[i]
            if not variant_option:
                continue

            attribute_group = self.attribute_groups[i]
            attribute_pair = AttributePair(
                attribute=attribute_group.get_attribute_by(variant_option),
                attribute_group=attribute_group,
            )
            attribute_pairs.append(attribute_pair)
        return attribute_pairs

    def parse_variant_specific_prices(
            self, variant_raw: dict
    ) -> Optional[List[SpecificPrice]]:
        """
        Parses the variant specific prices from the product data and returns a list of SpecificPrice dataclasses.

        Args:
          variant_raw: The variant data dictionary.

        Returns:
          A list of SpecificPrice dataclasses, or None if there are no specific prices.
        """

        _compare_at_price = variant_raw["compare_at_price"]
        _price = variant_raw["price"]

        if _compare_at_price:
            amount_reduction = Decimal(Decimal(_compare_at_price) - Decimal(_price))
            percent_reduction = (
                    amount_reduction / Decimal(_compare_at_price) * Decimal(100)
            )
            reduction_type = SpecificPriceType.AMOUNT
        else:
            amount_reduction = None
            percent_reduction = None
            reduction_type = None

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
        return [specific_price]

    def get_variant_images(self, variant_raw: dict) -> Optional[List[Image]]:
        """
        Gets the variant images from the product data and returns a list of Image dataclasses.

        Args:
          variant_raw: The variant data dictionary.

        Returns:
          A list of Image dataclasses, or None if there are no images.
        """

        image_id = variant_raw["image_id"]
        if image_id:
            for image in self.images:
                if image.id == image_id:
                    return [image]
        return None
