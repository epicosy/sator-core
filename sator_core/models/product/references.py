from typing import List, Optional, Iterator
from pydantic import BaseModel, Field, AnyUrl


class ProductReferences(BaseModel):
    product_id: str
    homepage: Optional[List[AnyUrl]] = Field(default_factory=list)
    repositories: Optional[List[AnyUrl]] = Field(default_factory=list)
    purls: Optional[List[AnyUrl]] = Field(default_factory=list)
    other: Optional[List[AnyUrl]] = Field(default_factory=list)

    def extend(self, references: "ProductReferences"):
        self.homepage = list(set(self.homepage + references.homepage))
        self.purls = list(set(self.purls + references.purls))
        self.repositories = list(set(self.repositories + references.repositories))
        self.other = list(set(self.other + references.other))

    def to_list(self) -> List[AnyUrl]:
        return self.homepage + self.purls + self.repositories + self.other

    def __iter__(self) -> Iterator[AnyUrl]:
        return iter(self.to_list())

    def __len__(self):
        return len(self.to_list())

    def __str__(self):
        ref_categories = [
            ("homepage", self.homepage),
            ("repositories", self.repositories),
            ("purls", self.purls),
            ("other", self.other)
        ]

        ref_details = [f"{len(ref)} {name}" for name, ref in ref_categories if ref]
        ref_str = f"{len(self)} references" + (" (" + ", ".join(ref_details) + ")" if ref_details else "")

        return ref_str
