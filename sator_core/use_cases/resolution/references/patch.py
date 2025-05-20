from typing import List

from sator_core.models.patch.references import PatchReferences

from sator_core.models.product.locator import ProductLocator
from sator_core.models.vulnerability.locator import VulnerabilityLocator

from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.repositories.oss import OSSRepositoryPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driving.resolution.references.patch import PatchReferencesResolutionPort


class PatchReferencesResolution(PatchReferencesResolutionPort):
    def __init__(
            self, oss_repositories: List[OSSRepositoryPort], oss_gateway: OSSGatewayPort,
            storage_port: StoragePersistencePort
    ):
        self.oss_repositories = oss_repositories
        self.oss_gateway = oss_gateway
        self.storage_port = storage_port

    def search_patch_references(self, vulnerability_id: str) -> PatchReferences | None:
        patch_references = self.storage_port.load(PatchReferences, vulnerability_id)

        if not patch_references:
            patch_references = self._get_patch_references(vulnerability_id)

            if patch_references:
                self.storage_port.save(patch_references, vulnerability_id)

        return patch_references

    def _get_patch_references(self, vulnerability_id: str) -> PatchReferences | None:
        patch_references = PatchReferences(
            vulnerability_id=vulnerability_id,
        )

        vulnerability_locator = self.storage_port.load(VulnerabilityLocator, vulnerability_id)
        product_locator = None

        if vulnerability_locator:
            product_locator = self.storage_port.load(ProductLocator, vulnerability_locator.product.id)

        # TODO: find a better way to do this
        for port in self.oss_repositories:
            references = port.get_references(
                vulnerability_id, vulnerability_locator=vulnerability_locator, product_locator=product_locator
            )

            if references:
                patch_references.extend(references)

        # TODO: also use the OSSGatewayPort to get references if needed

        return patch_references if len(patch_references) > 0 else None
