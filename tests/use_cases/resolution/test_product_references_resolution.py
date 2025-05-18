import unittest

from pydantic import AnyUrl
from unittest.mock import MagicMock

from sator_core.models.product import Product, ProductReferences
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.repositories.product import ProductRepositoryPort
from sator_core.use_cases.resolution.references.product import ProductReferencesResolution


test_product = Product(
    vendor="onlyoffice",
    name="document_server"
)

test_product_references = ProductReferences(
    product_id=test_product.id,
    homepage=[AnyUrl("https://onlyoffice.com")],
    repositories=[AnyUrl("https://github.com/ONLYOFFICE/DocumentServer")],
    purls=[AnyUrl("pkg:github/onlyoffice/documentserver")],
)


class TestProductReferencesResolution(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock(spec=StoragePersistencePort)
        self.mock_repo1 = MagicMock(spec=ProductRepositoryPort)
        self.mock_repo2 = MagicMock(spec=ProductRepositoryPort)
        self.resolution = ProductReferencesResolution(
            product_repositories=[self.mock_repo1, self.mock_repo2],
            storage_port=self.mock_storage
        )

    def test_returns_and_saves_cached_references(self):
        """Test returns cached references and saves them again"""
        self.mock_storage.load.return_value = test_product_references

        result = self.resolution.search_product_references(test_product.vendor, test_product.name)

        self.assertEqual(result, test_product_references)
        self.mock_storage.load.assert_called_once_with(ProductReferences, test_product.id)
        self.mock_storage.save.assert_called_once_with(test_product_references, test_product.id)
        self.mock_repo1.get_product_references.assert_not_called()
        self.mock_repo2.get_product_references.assert_not_called()

    def test_fetches_and_saves_new_references(self):
        """Test fetches references from repositories when not cached"""
        mock_refs1 = ProductReferences(
            product_id=test_product.id,
            homepage=test_product_references.homepage,
            purls=test_product_references.purls
        )
        mock_refs2 = ProductReferences(
            product_id=test_product.id,
            repositories=test_product_references.repositories
        )

        self.mock_storage.load.return_value = None
        self.mock_repo1.get_product_references.return_value = mock_refs1
        self.mock_repo2.get_product_references.return_value = mock_refs2

        result = self.resolution.search_product_references(test_product.vendor, test_product.name)

        self.assertEqual(result, test_product_references)
        self.mock_storage.save.assert_called_once_with(test_product_references, test_product.id)
        self.mock_repo1.get_product_references.assert_called_once_with(test_product)
        self.mock_repo2.get_product_references.assert_called_once_with(test_product)

    def test_returns_none_when_no_references_found(self):
        """Test returns None when no repositories have references"""
        self.mock_storage.load.return_value = None
        self.mock_repo1.get_product_references.return_value = ProductReferences(
            product_id="empty/product",
        )
        self.mock_repo2.get_product_references.return_value = ProductReferences(
            product_id="empty/product",
        )

        result = self.resolution.search_product_references("empty", "product")

        self.assertIsNone(result)
        self.mock_storage.save.assert_not_called()

    def test_handles_partial_repository_results(self):
        """Test combines results from repositories with partial responses"""
        mock_refs1 = ProductReferences(
            product_id="partial/results",
            homepage=test_product_references.homepage,
        )
        mock_refs2 = ProductReferences(
            product_id="partial/results"
        )

        self.mock_storage.load.return_value = None
        self.mock_repo1.get_product_references.return_value = mock_refs1
        self.mock_repo2.get_product_references.return_value = mock_refs2

        result = self.resolution.search_product_references("partial", "results")

        self.assertEqual(result, mock_refs1)
        self.mock_storage.save.assert_called_once_with(result, "partial/results")


if __name__ == "__main__":
    unittest.main()
