from abc import ABC, abstractmethod
from sator_core.models.oss.diff import Diff
from sator_core.models.patch.descriptor import DiffDescriptor


class DiffClassifierPort(ABC):
    @abstractmethod
    def classify_diff(self, diff: Diff) -> DiffDescriptor:
        raise NotImplementedError
