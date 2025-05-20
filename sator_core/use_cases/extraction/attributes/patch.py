from sator_core.models.patch.attributes import PatchAttributes
from sator_core.models.patch.references import PatchReferences

from sator_core.ports.driven.gateways.oss import OSSGatewayPort
from sator_core.ports.driven.persistence.storage import StoragePersistencePort
from sator_core.ports.driven.extraction.attributes.patch import PatchAttributesExtractorPort
from sator_core.ports.driving.extraction.attributes.patch import PatchAttributesExtractionPort


class PatchAttributesExtraction(PatchAttributesExtractionPort):
    def __init__(self, attributes_extractor: PatchAttributesExtractorPort, oss_gateway: OSSGatewayPort,
                 storage_port: StoragePersistencePort):
        self.oss_gateway = oss_gateway
        self.storage_port = storage_port
        self.attributes_extractor = attributes_extractor

    def extract_patch_attributes(self, vulnerability_id: str) -> PatchAttributes | None:
        patch_attributes = self.storage_port.load(PatchAttributes, vulnerability_id)

        if patch_attributes:
            return patch_attributes

        patch_references = self.storage_port.load(PatchReferences, vulnerability_id)

        if patch_references:
            for diff in patch_references.diffs:
                owner_id, repo_id, diff_id = self.oss_gateway.get_ids_from_url(str(diff))

                if diff_id is None:
                    continue

                diff = self.oss_gateway.get_diff(repo_id, diff_id)
                patch_attributes = self.attributes_extractor.extract_patch_attributes(diff)

                # TODO: decide if the patch attributes correspond/correlate with the vulnerability

                if patch_attributes:
                    self.storage_port.save(patch_attributes, vulnerability_id)
                    return patch_attributes

        return None
