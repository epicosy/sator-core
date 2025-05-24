from abc import ABC, abstractmethod
from typing import Union

from sator_core.models.patch.references import PatchReferences


class PatchReferencesResolutionPort(ABC):

    @abstractmethod
    def search_patch_references(self, vulnerability_id: str, product_id: str) -> Union[PatchReferences, None]:
        raise NotImplementedError
