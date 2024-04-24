from lambda_forge.builders.file_service import FileService


class DocsBuilder(FileService):
    @staticmethod
    def a_doc():
        return DocsBuilder()

    def with_config(self):

        self.config = f"""from infra.services import Services

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
"""
        return self

    def with_lambda_stack(self):
        self.lambda_stack = self.read_lines("infra/stacks/lambda_stack.py")
        self.lambda_stack.insert(0, f"from docs.config import DocsConfig\n")
        comment = "Docs"
        class_instance = f"        DocsConfig(self.services)\n"
        try:
            comment_index = self.lambda_stack.index(f"        # {comment}\n")
            self.lambda_stack.insert(comment_index + 1, class_instance)
        except:
            self.lambda_stack.append(f"\n")
            self.lambda_stack.append(f"        # {comment}\n")
            self.lambda_stack.append(class_instance)

        return self

    def build(self):
        folder_path = self.join("docs")
        self.make_dir(folder_path)
        self.make_file(folder_path, "__init__.py")
        self.make_file(folder_path, "config.py", self.config)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
