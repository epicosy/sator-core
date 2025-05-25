from typing import List, Optional

from sator_core.models.patch.attributes import PatchAttributes
from sator_core.models.patch.references import PatchReferences
from sator_core.models.product import ProductLocator

from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.extraction.attributes.patch import PatchAttributesExtractorPort
from sator_core.ports.driving.extraction.attributes.patch import PatchAttributesExtractionPort


class PatchAttributesExtraction(PatchAttributesExtractionPort):
    """
    Use case for extracting patch attributes from vulnerability references.
    """

    def __init__(self, attributes_extractor: PatchAttributesExtractorPort, oss_gateways: List[OSSGatewayPort],
                 storage_port: StoragePersistencePort):
        self.oss_gateways = oss_gateways
        self.storage_port = storage_port
        self.attributes_extractor = attributes_extractor

    def extract_patch_attributes(self, vulnerability_id: str, product_id: str) -> Optional[PatchAttributes]:
        """
        Extract patch attributes for a given vulnerability ID.

        Args:
            vulnerability_id: The ID of the vulnerability.
            product_id: The ID of the product.

        Returns:
            PatchAttributes if found or extracted successfully, None otherwise.
        """
        # Try to load cached patch attributes first
        cached_attributes = self._load_cached_attributes(vulnerability_id)
        if cached_attributes:
            return cached_attributes

        # Load patch references
        patch_references = self._load_patch_references(vulnerability_id)

        if not patch_references:
            return None

        # Load product locator
        product_locator = self._load_product_locator(product_id)

        if not product_locator:
            return None

        return self._process_diff_references(vulnerability_id, product_locator, patch_references)

    def _load_cached_attributes(self, vulnerability_id: str) -> Optional[PatchAttributes]:
        """
        Load cached patch attributes from storage.

        Args:
            vulnerability_id: The ID of the vulnerability.

        Returns:
            PatchAttributes if found in storage, None otherwise.
        """
        return self.storage_port.load(PatchAttributes, vulnerability_id)

    def _load_product_locator(self, product_id: str) -> Optional[ProductLocator]:
        """
        Load product locator from storage.

        Args:
            product_id: The ID of the product.

        Returns:
            ProductLocator if found in storage, None otherwise.
        """
        return self.storage_port.load(ProductLocator, product_id)

    def _load_patch_references(self, vulnerability_id: str) -> Optional[PatchReferences]:
        """
        Load patch references from storage.

        Args:
            vulnerability_id: The ID of the vulnerability.

        Returns:
            PatchReferences if found in storage, None otherwise.
        """
        return self.storage_port.load(PatchReferences, vulnerability_id)

    def _process_diff_references(self, vulnerability_id: str, product_locator: ProductLocator, 
                                patch_references: PatchReferences) -> Optional[PatchAttributes]:
        """
        Process diff references to find and extract patch attributes.

        Args:
            vulnerability_id: The ID of the vulnerability.
            product_locator: The product locator.
            patch_references: The patch references.

        Returns:
            PatchAttributes if extracted successfully, None otherwise.
        """
        for diff_url in patch_references.diffs:
            for oss_gateway in self.oss_gateways:
                # Get product repository IDs
                prod_owner_id, prod_repo_id = oss_gateway.get_ids_from_repo_path(
                    platform=product_locator.platform,repo_path=product_locator.repository_path
                )

                if prod_owner_id is None or prod_repo_id is None:
                    continue

                # Get diff IDs
                diff_owner_id, diff_repo_id, diff_id = oss_gateway.get_ids_from_url(str(diff_url))

                if diff_id is None:
                    continue

                # Check if diff is in the same repository or a submodule
                if not self._is_diff_in_repo_or_submodule(
                        oss_gateway, product_locator, prod_owner_id, prod_repo_id, diff_owner_id, diff_repo_id
                ):
                    continue

                # Get diff and extract attributes
                attributes = self._extract_and_save_attributes(oss_gateway, vulnerability_id, diff_repo_id, diff_id)

                if attributes:
                    return attributes

        return None

    def _is_diff_in_repo_or_submodule(
            self, oss_gateway: OSSGatewayPort, product_locator: ProductLocator, prod_owner_id: int, prod_repo_id: int,
            diff_owner_id: int, diff_repo_id: int
    ) -> bool:
        """
        Check if diff is in the same repository or a submodule.

        Args:
            oss_gateway: The OSS gateway.
            product_locator: The product locator.
            prod_owner_id: The product owner ID.
            prod_repo_id: The product repo ID.
            diff_owner_id: The diff owner ID.
            diff_repo_id: The diff repo ID.

        Returns:
            True if diff is in the same repository or a submodule, False otherwise.
        """
        # If diff is in the same repository, return True
        if prod_owner_id == diff_owner_id and prod_repo_id == diff_repo_id:
            return True

        # Check if diff is in a submodule
        return self._is_diff_in_submodule(oss_gateway, product_locator, diff_owner_id, diff_repo_id)

    def _is_diff_in_submodule(
            self, oss_gateway: OSSGatewayPort, product_locator: ProductLocator, diff_owner_id: int, diff_repo_id: int
    ) -> bool:
        """
        Check if diff is in a submodule.

        Args:
            oss_gateway: The OSS gateway.
            product_locator: The product locator.
            diff_owner_id: The diff owner ID.
            diff_repo_id: The diff repo ID.

        Returns:
            True if diff is in a submodule, False otherwise.
        """
        for component_path in oss_gateway.get_repo_submodules(
                platform=product_locator.platform, repo_path=product_locator.repository_path
        ):
            comp_owner_id, comp_repo_id = oss_gateway.get_ids_from_repo_path(
                platform=product_locator.platform, repo_path=component_path
            )

            if diff_owner_id == comp_owner_id and diff_repo_id == comp_repo_id:
                return True

        return False

    def _extract_and_save_attributes(
            self, oss_gateway: OSSGatewayPort, vulnerability_id: str, diff_repo_id: int, diff_id: str
    ) -> Optional[PatchAttributes]:
        """
        Extract and save patch attributes.

        Args:
            oss_gateway: The OSS gateway.
            vulnerability_id: The ID of the vulnerability.
            diff_repo_id: The diff repo ID.
            diff_id: The diff ID.

        Returns:
            PatchAttributes if extracted successfully, None otherwise.
        """
        diff = oss_gateway.get_diff(diff_repo_id, diff_id)
        patch_attributes = self.attributes_extractor.extract_patch_attributes(vulnerability_id, diff)

        # TODO: decide if the patch attributes correspond/correlate with the vulnerability

        if patch_attributes:
            self.storage_port.save(patch_attributes, vulnerability_id)
            return patch_attributes

        return None
