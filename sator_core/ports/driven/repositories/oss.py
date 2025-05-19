from typing import List
from abc import ABC, abstractmethod

from sator_core.models.oss.diff import Diff
from sator_core.models.product import ProductLocator
from sator_core.models.patch.references import PatchReferences
from sator_core.models.vulnerability import VulnerabilityLocator


class OSSRepositoryPort(ABC):
    @abstractmethod
    def get_diff(self, commit_sha: str) -> Diff | None:
        raise NotImplementedError

    @abstractmethod
    def get_diffs(self) -> List[Diff]:
        raise NotImplementedError

    @abstractmethod
    def get_references(
            self, vulnerability_id: str, vulnerability_locator: VulnerabilityLocator = None,
            product_locator: ProductLocator = None
    ) -> PatchReferences | None:
        """
            Method for getting patch references for a vulnerability.

            :param vulnerability_id: The ID of the vulnerability.
            :param vulnerability_locator: The locator of the vulnerability.
            :param product_locator: The locator of the product.
        """
        raise NotImplementedError
