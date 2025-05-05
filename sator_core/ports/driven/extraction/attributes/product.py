from abc import ABC, abstractmethod

from sator_core.models.product import ProductAttributes, ProductReferences


class ProductAttributesExtractorPort(ABC):
    @abstractmethod
    def extract_product_attributes(self, references: ProductReferences) -> ProductAttributes | None:
        """
            Method for extracting attributes from product references.
        """
        raise NotImplementedError
