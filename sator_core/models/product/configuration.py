from pydantic import BaseModel
from sator_core.models.product.product import Product


class Configuration(BaseModel):
    product: Product
    version: str

    @property
    def id(self):
        return f"{self.product.vendor}/{self.product.name}/{self.version}"

    def __hash__(self):
        return hash((self.product.name, self.product.vendor, self.version))

    def __eq__(self, other):
        if not isinstance(other, Configuration):
            return False

        return self.product == other.product and self.version == other.version

    def __str__(self):
        return self.id
