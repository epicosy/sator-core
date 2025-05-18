from abc import ABC, abstractmethod
from sator_core.models.product import ProductAttributes
from sator_core.models.enums import ProductPart, ProductType, LicenseType


class ProductClassifierPort(ABC):
    @abstractmethod
    def classify_product_part(self, product_attributes: ProductAttributes) -> ProductPart:
        """
            Classify the given product by part.

            Args:
                product_attributes: The product attributes.

            Returns:
                The product part.
        """
        raise NotImplementedError

    @abstractmethod
    def classify_product_type(self, product_attributes: ProductAttributes, part: ProductPart) -> ProductType:
        """
            Classify the given product by type.

            Args:
                product_attributes: The product attributes.
                part: The product part.

            Returns:
                The product type.
        """
        raise NotImplementedError

    @abstractmethod
    def classify_license_type(self, product_attributes: ProductAttributes) -> LicenseType:
        """
            Classify the given product by license type.

            Args:
                product_attributes: The product attributes.

            Returns:
                The product license type.
        """
        raise NotImplementedError
