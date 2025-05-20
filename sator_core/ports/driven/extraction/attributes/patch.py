from abc import ABC, abstractmethod

from sator_core.models.oss.diff import Diff
from sator_core.models.patch.attributes import PatchAttributes


class PatchAttributesExtractorPort(ABC):
    @abstractmethod
    def extract_patch_attributes(self, diff: Diff) -> PatchAttributes | None:
        """
            Method for extracting attributes from a vulnerability description.
        """
        raise NotImplementedError
