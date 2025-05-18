import unittest

from unittest.mock import MagicMock

from sator_core.models.product import Product
from sator_core.models.product.attributes import ProductAttributes
from sator_core.models.product.descriptor import ProductDescriptor
from sator_core.use_cases.annotation.attributes.product import ProductAttributesAnnotation

from sator_core.models.enums import LicenseType, ProductType, ProductPart


test_product = Product(
    vendor="onlyoffice",
    name="document_server"
)

test_product_attributes = ProductAttributes(
    name="Document Server",
    product_id=test_product.id,
    keywords=["online office suite", "collaborative editing"],
    platforms=["Mac", "Windows", "Linux"]
)


test_product_descriptor = ProductDescriptor(
    product_id=test_product.id,
    type=ProductType.SERVER,
    part=ProductPart.APPLICATION,
    license_type=LicenseType.OPEN_SOURCE
)


class TestProductAttributesAnnotation(unittest.TestCase):
    def setUp(self):
        self.mock_classifier = MagicMock()
        self.mock_storage = MagicMock()
        self.annotation = ProductAttributesAnnotation(
            product_classifier=self.mock_classifier,
            storage_port=self.mock_storage
        )

    def test_returns_cached_descriptor(self):
        self.mock_storage.load.return_value = test_product_descriptor

        result = self.annotation.annotate_product_attributes(test_product.id)
        self.assertEqual(result, test_product_descriptor)
        self.mock_storage.load.assert_called_once_with(ProductDescriptor, test_product.id)

    def test_creates_new_descriptor_from_attributes(self):
        # Mock storage responses
        self.mock_storage.load.side_effect = [None, test_product_attributes]

        # Configure classifier mocks
        self.mock_classifier.classify_product_part.return_value = ProductPart.APPLICATION
        self.mock_classifier.classify_product_type.return_value = ProductType.SERVER
        self.mock_classifier.classify_license_type.return_value = LicenseType.OPEN_SOURCE

        result = self.annotation.annotate_product_attributes(test_product.id)

        self.assertEqual(result, test_product_descriptor)
        self.mock_storage.save.assert_called_once_with(test_product_descriptor, test_product.id)

    def test_returns_none_when_no_attributes(self):
        self.mock_storage.load.return_value = None

        result = self.annotation.annotate_product_attributes("missing_id")
        self.assertIsNone(result)
        self.mock_storage.load.assert_any_call(ProductAttributes, "missing_id")
