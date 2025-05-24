import unittest

from pydantic import AnyUrl
from unittest.mock import MagicMock

from sator_core.models.patch.references import PatchReferences
from sator_core.models.product import Product, ProductLocator
from sator_core.models.vulnerability.locator import VulnerabilityLocator
from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.repositories.oss import OSSRepositoryPort
from sator_core.use_cases.resolution.references.patch import PatchReferencesResolution


test_vulnerability_id = "CVE-2023-30187"
test_product = Product(
    vendor="onlyoffice",
    name="document_server"
)


test_vulnerability_locator = VulnerabilityLocator(
    product=test_product,
    version="4.0.3",
    function="",
    file="",
)


test_product_locator = ProductLocator(
    product_id=test_product.id,
    platform="github",
    repository_path="ONLYOFFICE/DocumentServer",
)


test_patch_references = PatchReferences(
    vulnerability_id=test_vulnerability_id,
    diffs=[AnyUrl("https://github.com/ONLYOFFICE/core/commit/2b6ad83b36afd9845085b536969d366d1d61150a")],
    messages=[AnyUrl("https://github.com/ONLYOFFICE/core/pull/123")],
    other=[AnyUrl("https://example.com/patch-info")]
)


class TestPatchReferencesResolution(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock(spec=StoragePersistencePort)
        self.mock_oss_gateway1 = MagicMock(spec=OSSGatewayPort)
        self.mock_oss_gateway2 = MagicMock(spec=OSSGatewayPort)
        self.mock_repo1 = MagicMock(spec=OSSRepositoryPort)
        self.mock_repo2 = MagicMock(spec=OSSRepositoryPort)
        self.resolution = PatchReferencesResolution(
            oss_repositories=[self.mock_repo1, self.mock_repo2],
            oss_gateways=[self.mock_oss_gateway1, self.mock_oss_gateway2],
            storage_port=self.mock_storage
        )

    def test_returns_cached_references(self):
        """Test returns cached references from storage"""
        self.mock_storage.load.return_value = test_patch_references

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        self.assertEqual(result, test_patch_references)
        self.mock_storage.load.assert_called_once_with(PatchReferences, test_vulnerability_id)
        self.mock_repo1.get_references.assert_not_called()
        self.mock_repo2.get_references.assert_not_called()

    def test_fetches_and_saves_new_references(self):
        """Test fetches references from repositories when not cached"""
        mock_refs1 = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            diffs=test_patch_references.diffs,
            messages=test_patch_references.messages
        )
        mock_refs2 = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            other=test_patch_references.other
        )

        # First load returns None for patch references
        # Second load returns vulnerability locator
        # Third load returns product locator
        self.mock_storage.load.side_effect = [None, test_vulnerability_locator, test_product_locator]
        self.mock_repo1.get_references.return_value = mock_refs1
        self.mock_repo2.get_references.return_value = mock_refs2

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        self.assertEqual(result, test_patch_references)
        self.mock_storage.save.assert_called_once_with(test_patch_references, test_vulnerability_id)
        self.mock_repo1.get_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )
        self.mock_repo2.get_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )

    def test_returns_none_when_no_references_found(self):
        """Test returns None when no repositories have references"""
        empty_refs = PatchReferences(
            vulnerability_id=test_vulnerability_id
        )

        # First load returns None for patch references
        # Second load returns vulnerability locator
        # Third load returns product locator
        self.mock_storage.load.side_effect = [None, test_vulnerability_locator, test_product_locator]
        self.mock_repo1.get_references.return_value = empty_refs
        self.mock_repo2.get_references.return_value = empty_refs
        self.mock_oss_gateway1.search_patch_references.return_value = None
        self.mock_oss_gateway2.search_patch_references.return_value = None

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        self.assertIsNone(result)
        self.mock_storage.save.assert_not_called()

    def test_handles_partial_repository_results(self):
        """Test combines results from repositories with partial responses"""
        mock_refs1 = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            diffs=test_patch_references.diffs
        )
        mock_refs2 = PatchReferences(
            vulnerability_id=test_vulnerability_id
        )

        # First load returns None for patch references
        # Second load returns vulnerability locator
        # Third load returns product locator
        self.mock_storage.load.side_effect = [None, test_vulnerability_locator, test_product_locator]
        self.mock_repo1.get_references.return_value = mock_refs1
        self.mock_repo2.get_references.return_value = mock_refs2
        # No need to call OSS gateways since repositories return references

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        self.assertEqual(result, mock_refs1)
        self.mock_storage.save.assert_called_once_with(result, test_vulnerability_id)

    def test_handles_missing_locators(self):
        """Test handles case when vulnerability or product locators are missing"""
        # First load returns None for patch references
        # Second load returns None for vulnerability locator
        # Third load returns None for product locator (not used in this test since we return early)
        self.mock_storage.load.side_effect = [None, None, None]

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        # In the new implementation, if locators can't be found, the method returns None
        self.assertIsNone(result)
        self.mock_storage.save.assert_not_called()
        self.mock_repo1.get_references.assert_not_called()
        self.mock_repo2.get_references.assert_not_called()
        self.mock_oss_gateway1.search_patch_references.assert_not_called()
        self.mock_oss_gateway2.search_patch_references.assert_not_called()

    def test_uses_gateways_when_repositories_return_none(self):
        """Test uses OSS gateways when repositories return no references"""
        empty_refs = PatchReferences(
            vulnerability_id=test_vulnerability_id
        )

        gateway_refs1 = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            diffs=test_patch_references.diffs
        )

        gateway_refs2 = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            messages=test_patch_references.messages,
            other=test_patch_references.other
        )

        # First load returns None for patch references
        # Second load returns vulnerability locator
        # Third load returns product locator
        self.mock_storage.load.side_effect = [None, test_vulnerability_locator, test_product_locator]

        # Repositories return empty references
        self.mock_repo1.get_references.return_value = empty_refs
        self.mock_repo2.get_references.return_value = empty_refs

        # Gateways return references
        self.mock_oss_gateway1.search_patch_references.return_value = gateway_refs1
        self.mock_oss_gateway2.search_patch_references.return_value = gateway_refs2

        result = self.resolution.search_patch_references(test_vulnerability_id, test_product.id)

        # Result should be the combined references from both gateways
        expected_result = PatchReferences(
            vulnerability_id=test_vulnerability_id,
            diffs=test_patch_references.diffs,
            messages=test_patch_references.messages,
            other=test_patch_references.other
        )

        self.assertEqual(result, expected_result)
        self.mock_storage.save.assert_called_once_with(expected_result, test_vulnerability_id)

        # Verify repositories were called
        self.mock_repo1.get_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )
        self.mock_repo2.get_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )

        # Verify gateways were called
        self.mock_oss_gateway1.search_patch_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )
        self.mock_oss_gateway2.search_patch_references.assert_called_once_with(
            test_vulnerability_id,
            vulnerability_locator=test_vulnerability_locator,
            product_locator=test_product_locator
        )


if __name__ == "__main__":
    unittest.main()
