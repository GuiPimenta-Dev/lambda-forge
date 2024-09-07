from infra.services import Services


class DocsConfig:
    def __init__(self, services: Services) -> None:
        # Swagger at /swagger
        services.api_gateway.create_docs(
            endpoint="/swagger", artifact="swagger", public=True
        )

        # Redoc at /redoc
        services.api_gateway.create_docs(
            endpoint="/redoc", artifact="redoc", public=True
        )
