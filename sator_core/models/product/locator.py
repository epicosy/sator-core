from pydantic import BaseModel


class ProductLocator(BaseModel):
    product_id: str
    platform: str
    repository_path: str

    def __hash__(self):
        return hash((self.product_id, self.platform, self.repository_path))

    def __eq__(self, other):
        if not isinstance(other, ProductLocator):
            return False

        return self.product_id == other.product_id and self.platform == other.platform and self.repository_path == other.repository_path

    def __str__(self):
        return f"{self.product_id} | {self.platform} | {self.repository_path}"
