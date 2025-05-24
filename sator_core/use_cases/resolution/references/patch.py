from typing import List, Union

from sator_core.models.patch.references import PatchReferences

from sator_core.models.product.locator import ProductLocator
from sator_core.models.vulnerability.locator import VulnerabilityLocator

from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.repositories.oss import OSSRepositoryPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driving.resolution.references.patch import PatchReferencesResolutionPort


class PatchReferencesResolution(PatchReferencesResolutionPort):
    def __init__(
            self, oss_repositories: List[OSSRepositoryPort], oss_gateways: List[OSSGatewayPort],
            storage_port: StoragePersistencePort
    ):
        self.oss_repositories = oss_repositories
        self.oss_gateways = oss_gateways
        self.storage_port = storage_port

    def search_patch_references(self, vulnerability_id: str, product_id: str) -> Union[PatchReferences, None]:
        patch_references = self.storage_port.load(PatchReferences, vulnerability_id)

        if not patch_references:
            vulnerability_locator = self.storage_port.load(VulnerabilityLocator, vulnerability_id)
            product_locator = self.storage_port.load(ProductLocator, product_id)

            if not vulnerability_locator or not product_locator:
                # If we cannot find the locators, we cannot proceed
                return None

            patch_references = self._get_patch_references(
                vulnerability_id=vulnerability_id,
                vulnerability_locator=vulnerability_locator,
                product_locator=product_locator
            )

            if not patch_references:
                patch_references = self._search_patch_references(
                    vulnerability_id=vulnerability_id,
                    vulnerability_locator=vulnerability_locator,
                    product_locator=product_locator
                )

            if patch_references:
                self.storage_port.save(patch_references, vulnerability_id)

        return patch_references

    def _get_patch_references(
            self, vulnerability_id: str, vulnerability_locator: VulnerabilityLocator, product_locator: ProductLocator
    ) -> Union[PatchReferences, None]:

        patch_references = PatchReferences(
            vulnerability_id=vulnerability_id,
        )

        for port in self.oss_repositories:
            references = port.get_references(
                vulnerability_id, vulnerability_locator=vulnerability_locator, product_locator=product_locator
            )

            if references:
                patch_references.extend(references)

        return patch_references if len(patch_references) > 0 else None

    def _search_patch_references(
            self, vulnerability_id: str, vulnerability_locator: VulnerabilityLocator, product_locator: ProductLocator
    ) -> Union[PatchReferences, None]:
        patch_references = PatchReferences(
            vulnerability_id=vulnerability_id,
        )

        for port in self.oss_gateways:
            references = port.search_patch_references(
                vulnerability_id, vulnerability_locator=vulnerability_locator, product_locator=product_locator
            )

            if references:
                patch_references.extend(references)

        return patch_references if len(patch_references) > 0 else None
