from sator_core.models.product import Product, ProductAttributes, ProductReferences

from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.extraction.attributes.product import ProductAttributesExtractorPort
from sator_core.ports.driving.extraction.attributes.product import ProductAttributesExtractionPort


class ProductAttributesExtraction(ProductAttributesExtractionPort):
    def __init__(self, extractor_port: ProductAttributesExtractorPort, storage_port: StoragePersistencePort):
        self.extractor_port = extractor_port
        self.storage_port = storage_port

    def extract_product_attributes(self, vendor: str, name: str) -> ProductAttributes | None:
        product = Product(vendor=vendor, name=name)
        product_attributes = self.storage_port.load(ProductAttributes, product.id)

        if product_attributes:
            return product_attributes

        product_references = self.storage_port.load(ProductReferences, product.id)

        if product_references:
            product_attributes = self.extractor_port.extract_product_attributes(product, product_references)

            if product_attributes:
                self.storage_port.save(product_attributes, product.id)
                return product_attributes

        return None
