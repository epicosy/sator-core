from typing import List
from abc import ABC, abstractmethod

from sator_core.models.product import Product, Configuration
from sator_core.models.product.references import ProductReferences
from sator_core.models.enums import ProductPart, ProductType


class ProductRepositoryPort(ABC):
    @abstractmethod
    def get_vendor_products(self, vendor_name: str) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_product(self, vendor_name: str, product_name: str) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def search(self, vendor_name: str, product_name: str, n: int = 10) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def search_config_by_str(self, configuration: str) -> Configuration | None:
        """
            Extracts the configuration from a string and looks up for the product/version.

        :param configuration: The configuration string.
        :return: The extracted configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_version(self, product: Product, version: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def get_versions(self, product: Product) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_product_references(self, product: Product) -> ProductReferences:
        raise NotImplementedError

    @abstractmethod
    def get_product_part(self, product: Product) -> ProductPart:
        raise NotImplementedError

    @abstractmethod
    def get_product_type(self, product: Product) -> ProductType:
        raise NotImplementedError
