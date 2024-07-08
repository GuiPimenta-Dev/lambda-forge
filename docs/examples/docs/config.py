from infra.services import Services


class DocsConfig:
    def __init__(self, services: Services) -> None:
        # Swagger at /swagger
        services.api_gateway.create_docs(endpoint="/swagger", artifact="swagger", public=True)

        # Redoc at /redoc
        services.api_gateway.create_docs(endpoint="/redoc", artifact="redoc", public=True)

        # Architecture Diagram at /diagram
        services.api_gateway.create_docs(endpoint="/diagram", artifact="diagram", public=True, stages=["Prod"])

        # Tests Report at /tests
        services.api_gateway.create_docs(endpoint="/tests", artifact="tests", public=True, stages=["Staging"])

        # Coverage Report at /coverage
        services.api_gateway.create_docs(endpoint="/coverage", artifact="coverage", public=True, stages=["Staging"])
