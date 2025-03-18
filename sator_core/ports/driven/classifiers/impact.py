from typing import List
from abc import ABC, abstractmethod

from sator_core.models.enums import ImpactType
from sator_core.models.vulnerability.attributes import VulnerabilityAttributes


class ImpactClassifierPort(ABC):
    @abstractmethod
    def classify_impact(self, vulnerability_details: VulnerabilityAttributes) -> List[ImpactType]:
        """
            Classify the impact of a vulnerability based on its details.
        """
        raise NotImplementedError
