from abc import ABC, abstractmethod

from sator_core.models.product.attributes import ProductAttributes


class ProductAttributesExtractionPort(ABC):
    @abstractmethod
    def extract_product_attributes(self, vendor: str, name: str) -> ProductAttributes | None:
        raise NotImplementedError
