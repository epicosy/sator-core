import unittest

from pydantic import AnyUrl
from unittest.mock import MagicMock
from sator_core.models.product import Product, ProductAttributes, ProductReferences
from sator_core.use_cases.extraction.attributes import ProductAttributesExtraction


test_product = Product(
    vendor="vendor",
    name="product",
)

test_prod_references = ProductReferences(
    product_id=test_product.id,
    homepage=[AnyUrl("https://example.com")],
    repositories=[AnyUrl("https://example.com/repository")],
    other=[AnyUrl("https://example.com/releases")]
)

test_product_attributes = ProductAttributes(
    name="product",
    product_id=test_product.id,
    keywords=["keyword1", "keyword2"],
    platforms=["linux", "macos", "windows"],
)


class TestProductAttributesExtraction(unittest.TestCase):
    def setUp(self):
        self.mock_extractor = MagicMock()
        self.mock_storage = MagicMock()
        self.extractor = ProductAttributesExtraction(
            extractor_port=self.mock_extractor,
            storage_port=self.mock_storage
        )

    def test_returns_cached_attributes(self):
        self.mock_storage.load.side_effect = lambda cls, _id: test_product_attributes if cls == ProductAttributes else None
        result = self.extractor.extract_product_attributes("vendor", "product")
        self.assertEqual(result, test_product_attributes)

    def test_extracts_and_saves_attributes_when_references_exist(self):
        self.mock_storage.load.side_effect = lambda cls, _id: test_prod_references if cls == ProductReferences else None
        self.mock_extractor.extract_product_attributes.return_value = test_product_attributes
        result = self.extractor.extract_product_attributes("vendor", "product")
        self.assertEqual(result, test_product_attributes)
        self.mock_storage.save.assert_called_once_with(test_product_attributes, "vendor/product")

    def test_returns_none_when_no_data(self):
        self.mock_storage.load.return_value = None
        result = self.extractor.extract_product_attributes("vendor", "product")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
