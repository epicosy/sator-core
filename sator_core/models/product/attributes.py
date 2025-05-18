from typing import List
from pydantic import BaseModel, Field


class ProductAttributes(BaseModel):
    name: str
    product_id: str
    keywords: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)

    def __str__(self):
        return f"{self.product_id} with {len(self.keywords)} keywords and {len(self.platforms)} platforms"
