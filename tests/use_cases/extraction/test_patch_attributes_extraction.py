import unittest
from datetime import datetime
from unittest.mock import MagicMock

from pydantic import AnyUrl

from sator_core.models.oss.diff import Diff, Patch, DiffHunk, DiffLine
from sator_core.models.patch.attributes import PatchAttributes
from sator_core.models.patch.references import PatchReferences
from sator_core.models.product import ProductLocator
from sator_core.use_cases.extraction.attributes.patch import PatchAttributesExtraction


# Test data
test_vulnerability_id = "CVE-2023-12345"

test_diff = Diff(
    repository_id=123,
    message="Fix security vulnerability",
    date=datetime.now(),
    commit_sha="abc123",
    parent_commit_sha="def456",
    patches=[
        Patch(
            old_file="src/vulnerable_file.py",
            new_file="src/fixed_file.py",
            hunks=[
                DiffHunk(
                    order=1,
                    old_start=10,
                    old_lines=[DiffLine(type="-", lineno=10, content="vulnerable code")],
                    new_start=10,
                    new_lines=[DiffLine(type="+", lineno=10, content="fixed code")]
                )
            ]
        )
    ]
)

test_patch_references = PatchReferences(
    vulnerability_id=test_vulnerability_id,
    diffs=[AnyUrl("https://github.com/example/repo/commit/abc123")]
)

test_patch_attributes = PatchAttributes(
    vulnerability_id=test_vulnerability_id,
    action="fix",
    flaw="buffer overflow",
    version="1.2.3",
    sec_words=["vulnerability", "security"],
    diff=test_diff
)

test_product_locator = ProductLocator(
    product_id="example/product",
    platform="github",
    repository_path="example/repo"
)


class TestPatchAttributesExtraction(unittest.TestCase):
    def setUp(self):
        self.mock_attributes_extractor = MagicMock()
        self.mock_oss_gateway = MagicMock()
        self.mock_storage = MagicMock()
        self.extractor = PatchAttributesExtraction(
            attributes_extractor=self.mock_attributes_extractor,
            oss_gateways=[self.mock_oss_gateway],
            storage_port=self.mock_storage
        )

    def test_returns_cached_attributes(self):
        self.mock_storage.load.side_effect = [test_patch_attributes]

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertEqual(result, test_patch_attributes)
        # Verify storage was queried but no extraction was performed
        self.mock_storage.load.assert_any_call(PatchAttributes, test_vulnerability_id)
        self.mock_attributes_extractor.extract_patch_attributes.assert_not_called()

    def test_extracts_and_saves_attributes_when_references_exist(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, test_product_locator]
        self.mock_oss_gateway.get_ids_from_repo_path.return_value = (1, 123)
        self.mock_oss_gateway.get_ids_from_url.return_value = (1, 123, "abc123")
        self.mock_oss_gateway.get_diff.return_value = test_diff
        self.mock_attributes_extractor.extract_patch_attributes.return_value = test_patch_attributes
        # Ensure _is_diff_in_repo_or_submodule returns True
        self.mock_oss_gateway.get_repo_submodules.return_value = []

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertEqual(result, test_patch_attributes)
        self.mock_storage.save.assert_called_once_with(test_patch_attributes, test_vulnerability_id)
        self.mock_oss_gateway.get_ids_from_repo_path.assert_called_once_with(
            platform=test_product_locator.platform, repo_path=test_product_locator.repository_path
        )
        self.mock_oss_gateway.get_ids_from_url.assert_called_once()
        self.mock_oss_gateway.get_diff.assert_called_once_with(123, "abc123")
        self.mock_attributes_extractor.extract_patch_attributes.assert_called_once_with(test_vulnerability_id, test_diff)

    def test_returns_none_when_no_valid_diff_id(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, test_product_locator]
        self.mock_oss_gateway.get_ids_from_repo_path.return_value = (1, 123)
        self.mock_oss_gateway.get_ids_from_url.return_value = (1, 123, None)
        # Ensure _is_diff_in_repo_or_submodule returns True
        self.mock_oss_gateway.get_repo_submodules.return_value = []

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertIsNone(result)
        self.mock_oss_gateway.get_diff.assert_not_called()
        self.mock_attributes_extractor.extract_patch_attributes.assert_not_called()

    def test_returns_none_when_no_attributes_extracted(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, test_product_locator]
        self.mock_oss_gateway.get_ids_from_repo_path.return_value = (1, 123)
        self.mock_oss_gateway.get_ids_from_url.return_value = (1, 123, "abc123")
        self.mock_oss_gateway.get_diff.return_value = test_diff
        self.mock_attributes_extractor.extract_patch_attributes.return_value = None
        # Ensure _is_diff_in_repo_or_submodule returns True
        self.mock_oss_gateway.get_repo_submodules.return_value = []

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertIsNone(result)
        self.mock_storage.save.assert_not_called()

    def test_returns_none_when_no_data(self):
        # Setup: Storage returns no data
        self.mock_storage.load.return_value = None

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertIsNone(result)
        self.mock_oss_gateway.get_ids_from_url.assert_not_called()
        self.mock_oss_gateway.get_diff.assert_not_called()
        self.mock_attributes_extractor.extract_patch_attributes.assert_not_called()

    def test_returns_none_when_no_product_locator(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, None]

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertIsNone(result)
        self.mock_oss_gateway.get_ids_from_repo_path.assert_not_called()
        self.mock_oss_gateway.get_ids_from_url.assert_not_called()
        self.mock_oss_gateway.get_diff.assert_not_called()
        self.mock_attributes_extractor.extract_patch_attributes.assert_not_called()

    def test_extracts_attributes_when_diff_in_submodule(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, test_product_locator]
        self.mock_oss_gateway.get_ids_from_repo_path.side_effect = [
            (1, 123),  # For product repository
            (2, 456)   # For submodule repository
        ]
        self.mock_oss_gateway.get_ids_from_url.return_value = (2, 456, "abc123")  # Different owner/repo than product
        self.mock_oss_gateway.get_repo_submodules.return_value = ["submodule/repo"]
        self.mock_oss_gateway.get_diff.return_value = test_diff
        self.mock_attributes_extractor.extract_patch_attributes.return_value = test_patch_attributes

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        self.mock_oss_gateway.get_ids_from_repo_path.assert_any_call(
            platform=test_product_locator.platform, repo_path=test_product_locator.repository_path
        )
        self.mock_oss_gateway.get_repo_submodules.assert_called_once_with(
            platform=test_product_locator.platform, repo_path=test_product_locator.repository_path
        )
        self.mock_oss_gateway.get_ids_from_repo_path.assert_any_call(
            platform=test_product_locator.platform, repo_path="submodule/repo"
        )

        self.mock_oss_gateway.get_diff.assert_called_once_with(456, "abc123")
        self.mock_attributes_extractor.extract_patch_attributes.assert_called_once_with(test_vulnerability_id, test_diff)

        # Assert
        self.mock_storage.save.assert_called_once_with(test_patch_attributes, test_vulnerability_id)
        self.assertEqual(result, test_patch_attributes)

    def test_returns_none_when_diff_not_in_repo_or_submodule(self):
        self.mock_storage.load.side_effect = [None, test_patch_references, test_product_locator]
        self.mock_oss_gateway.get_ids_from_repo_path.return_value = (1, 123)  # For product repository
        self.mock_oss_gateway.get_ids_from_url.return_value = (3, 789, "xyz456")  # Different owner/repo than product
        self.mock_oss_gateway.get_repo_submodules.return_value = []  # No submodules

        # Execute
        result = self.extractor.extract_patch_attributes(test_vulnerability_id, test_product_locator.product_id)

        # Assert
        self.assertIsNone(result)
        self.mock_oss_gateway.get_diff.assert_not_called()
        self.mock_attributes_extractor.extract_patch_attributes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
