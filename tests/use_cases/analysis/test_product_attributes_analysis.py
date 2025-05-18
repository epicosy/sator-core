import unittest
from unittest.mock import MagicMock

from pydantic import AnyUrl

from sator_core.models.product import Product, ProductAttributes, ProductReferences, ProductLocator
from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.use_cases.analysis.attributes.product import ProductAttributesAnalysis


# Test data
test_product = Product(
    vendor="vendor",
    name="product"
)

test_product_attributes = ProductAttributes(
    name="product",
    product_id=test_product.id,
    keywords=["keyword1", "keyword2"],
    platforms=["linux", "macos", "windows"]
)

test_product_references = ProductReferences(
    product_id=test_product.id,
    homepage=[AnyUrl("https://example.com")],
    repositories=[AnyUrl("https://github.com/vendor/product")],
    purls=[AnyUrl("pkg:github/vendor/product")]
)

test_product_locator = ProductLocator(
    product_id="vendor/product",
    platform="linux",
    repository_path="vendor/product"
)


class TestProductAttributesAnalysis(unittest.TestCase):
    def setUp(self):
        self.mock_oss_gateway = MagicMock(spec=OSSGatewayPort)
        self.mock_storage = MagicMock(spec=StoragePersistencePort)
        self.analysis = ProductAttributesAnalysis(
            oss_gateway=self.mock_oss_gateway,
            storage_port=self.mock_storage
        )

    def test_returns_cached_locator(self):
        """Test returns cached locator when it exists in storage"""
        self.mock_storage.load.return_value = test_product_locator

        result = self.analysis.analyze_product_attributes("vendor/product")

        self.assertEqual(result, test_product_locator)
        self.mock_storage.load.assert_called_once_with(ProductLocator, "vendor/product")
        self.mock_oss_gateway.get_product_locator_from_urls.assert_not_called()

    def test_creates_and_saves_locator_when_attributes_and_references_exist(self):
        """Test creates and saves locator when attributes and references exist but locator is not cached"""
        # First load returns None (no cached locator)
        # Second load returns product_attributes
        # Third load returns product_references
        self.mock_storage.load.side_effect = [
            None,
            test_product_attributes,
            test_product_references
        ]
        self.mock_oss_gateway.get_product_locator_from_urls.return_value = test_product_locator

        result = self.analysis.analyze_product_attributes("vendor/product")

        self.assertEqual(result, test_product_locator)
        self.mock_oss_gateway.get_product_locator_from_urls.assert_called_once_with(
            "vendor/product",
            urls=test_product_references.repositories + test_product_references.purls,
            product_attributes=test_product_attributes
        )
        self.mock_storage.save.assert_called_once_with(test_product_locator, "vendor/product")

    def test_returns_none_when_no_attributes(self):
        """Test returns None when no product attributes exist"""
        # First load returns None (no cached locator)
        # Second load returns None (no product attributes)
        self.mock_storage.load.side_effect = [None, None]

        result = self.analysis.analyze_product_attributes("vendor/product")

        self.assertIsNone(result)
        self.mock_oss_gateway.get_product_locator_from_urls.assert_not_called()
        self.mock_storage.save.assert_not_called()

    def test_returns_none_when_no_references(self):
        """Test returns None when product attributes exist but no references"""
        # First load returns None (no cached locator)
        # Second load returns product_attributes
        # Third load returns None (no product references)
        self.mock_storage.load.side_effect = [None, test_product_attributes, None]

        result = self.analysis.analyze_product_attributes("vendor/product")

        self.assertIsNone(result)
        self.mock_oss_gateway.get_product_locator_from_urls.assert_not_called()
        self.mock_storage.save.assert_not_called()

    def test_returns_none_when_gateway_returns_no_locator(self):
        """Test returns None when OSS gateway cannot find a locator"""
        # First load returns None (no cached locator)
        # Second load returns product_attributes
        # Third load returns product_references
        self.mock_storage.load.side_effect = [
            None,
            test_product_attributes,
            test_product_references
        ]
        self.mock_oss_gateway.get_product_locator_from_urls.return_value = None

        result = self.analysis.analyze_product_attributes("vendor/product")

        self.assertIsNone(result)
        self.mock_oss_gateway.get_product_locator_from_urls.assert_called_once_with(
            "vendor/product",
            urls=test_product_references.repositories + test_product_references.purls,
            product_attributes=test_product_attributes
        )
        self.mock_storage.save.assert_not_called()


if __name__ == "__main__":
    unittest.main()