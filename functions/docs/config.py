
from infra.services import Services

class DocsConfig:

    def __init__(self, scope, services: Services) -> None:
        bucket = scope.node.try_get_context("bucket")
        services.api_gateway.create_docs(bucket=bucket, authorizer="docs_authorizer")
