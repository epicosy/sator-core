from typing import Optional
from abc import ABC, abstractmethod

from sator_core.models.patch.attributes import PatchAttributes


class PatchAttributesExtractionPort(ABC):
    @abstractmethod
    def extract_patch_attributes(self, vulnerability_id: str, product_id: str) -> Optional[PatchAttributes]:
        raise NotImplementedError
