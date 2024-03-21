
from infra.services import Services

class DocsConfig:

    def __init__(self, services: Services) -> None:
        services.api_gateway.create_docs(authorizer="docs_authorizer")
