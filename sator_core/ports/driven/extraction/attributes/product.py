from abc import ABC, abstractmethod

from sator_core.models.product import Product, ProductAttributes, ProductReferences


class ProductAttributesExtractorPort(ABC):
    @abstractmethod
    def extract_product_attributes(self, product: Product, references: ProductReferences) -> ProductAttributes | None:
        """
            Method for extracting attributes from product references.
        """
        raise NotImplementedError
