from abc import ABC, abstractmethod

from sator_core.models.product.metadata import ProductMetadata


class ProductMetadataResolutionPort(ABC):
    @abstractmethod
    def resolve_metadata(self, name: str, vendor: str) -> ProductMetadata | None:
        """Method for getting a vulnerability by its ID."""
        raise NotImplementedError
