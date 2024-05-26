from abc import ABC, abstractmethod
from typing import Dict, List


class IAWSLambda(ABC):
    @abstractmethod
    def create_function(
        self,
        name: str,
        path: str,
        description: str,
        directory: str,
        timeout: int,
        layers: List[str],
        environment: Dict[str, str],
    ) -> dict:
        pass


class IAPIGateway(ABC):
    @abstractmethod
    def create_trigger(self, method: str, path: str, function: str, public: bool, authorizer: str) -> dict:
        pass

    @abstractmethod
    def create_authorizer(self, function: str, name: str, default: bool) -> dict:
        pass

    @abstractmethod
    def create_docs(self, enabled: bool, authorizer: str) -> dict:
        pass
