from sator_core.models.product.attributes import ProductAttributes
from sator_core.models.product.references import ProductReferences

from sator_core.models.product.locator import ProductLocator

from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driving.analysis.attributes.product import ProductAttributesAnalysisPort


class ProductAttributesAnalysis(ProductAttributesAnalysisPort):
    def __init__(self, oss_gateway: OSSGatewayPort, storage_port: StoragePersistencePort):
        self.oss_gateway = oss_gateway
        self.storage_port = storage_port

    def analyze_product_attributes(self, product_id: str) -> ProductLocator | None:
        product_locator = self.storage_port.load(ProductLocator, product_id)

        if product_locator:
            return product_locator

        product_attributes = self.storage_port.load(ProductAttributes, product_id)

        if product_attributes:
            product_references = self.storage_port.load(ProductReferences, product_id)

            if product_references:
                locator = self.oss_gateway.get_product_locator_from_urls(
                    product_id, urls=product_references.repositories + product_references.purls,
                    product_attributes=product_attributes
                )

                if locator:
                    self.storage_port.save(locator, product_id)
                    return locator

        return None
