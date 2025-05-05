from abc import ABC, abstractmethod

from sator_core.models.product.references import ProductReferences


class ProductReferencesResolutionPort(ABC):

    @abstractmethod
    def search_product_references(self, vendor: str, name: str) -> ProductReferences | None:
        raise NotImplementedError
