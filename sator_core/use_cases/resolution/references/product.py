from typing import List

from sator_core.models.product import Product
from sator_core.models.product.references import ProductReferences

from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.repositories.product import ProductRepositoryPort
from sator_core.ports.driving.resolution.references.product import ProductReferencesResolutionPort


class ProductReferencesResolution(ProductReferencesResolutionPort):
    def __init__(self, product_repositories: List[ProductRepositoryPort], storage_port: StoragePersistencePort):
        self.product_repositories = product_repositories
        self.storage_port = storage_port

    def search_product_references(self, vendor: str, name: str) -> ProductReferences | None:
        product = Product(vendor=vendor, name=name)
        product_references = self.storage_port.load(ProductReferences, product.id)

        if not product_references:
            product_references = self._get_product_references(product)

        if product_references:
            self.storage_port.save(product_references, product.id)

        return product_references

    def _get_product_references(self, product: Product) -> ProductReferences | None:
        product_references = ProductReferences(
            product_id=product.id,
        )

        for port in self.product_repositories:
            references = port.get_product_references(product)

            if references:
                product_references.extend(references)

        return product_references if len(product_references) > 0 else None
