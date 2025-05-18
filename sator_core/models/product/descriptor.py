from pydantic import BaseModel
from sator_core.models.product import Product
from sator_core.models.enums import ProductPart, ProductType, LicenseType


class ProductDescriptor(BaseModel):
    product_id: str
    type: ProductType = ProductType.UNDEFINED
    part: ProductPart = ProductPart.UNDEFINED
    license_type: LicenseType = LicenseType.UNDEFINED

    def __hash__(self):
        return hash((self.product_id, self.type, self.part, self.license_type))

    def __eq__(self, other):
        if not isinstance(other, ProductDescriptor):
            return False

        return (self.product_id == other.product_id and self.type == other.type and self.part == other.part and
                self.license_type == other.license_type)
