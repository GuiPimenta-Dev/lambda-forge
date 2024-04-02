from lambda_forge.builders.file_service import FileService


class LayerBuilder(FileService):
    @staticmethod
    def a_layer():
        return LayerBuilder()
  
    def __init__(self) -> None:
        self.services = self.read_lines("infra/services/__init__.py")
    
    def with_layers(self):
        f = """from aws_cdk import aws_lambda as _lambda
from lambda_forge import Path


class Layers:
    def __init__(self, scope) -> None:

        self.layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="Layer",
            layer_version_arn="",
        )
"""     
        file_exists = self.file_exists("infra/services/layers.py")
        if not file_exists:
            self.make_file("infra/services", "layers.py", f)
            self.update_services(
                "from infra.services.layers import Layers", "self.layers = Layers(scope)"
            )

        return self
  
    def with_custom_layers(self, name, description):
        layers_lines = self.read_lines("infra/services/layers.py")

        layers_lines.append(f"\n")
        layers_lines.append(f"        self.{name}_layer = _lambda.LayerVersion(\n")
        layers_lines.append(f"            scope,\n")
        layers_lines.append(f"            id='{name.title().replace('_','')}Layer',\n")
        layers_lines.append(f"            code=_lambda.Code.from_asset(Path.layer('layers/{name}')),\n")
        layers_lines.append(f"            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],\n")
        layers_lines.append(f"            description='{description}',\n")
        layers_lines.append("         )\n")


        self.write_lines("infra/services/layers.py", layers_lines)
        return self

    def update_services(self, import_statement, instance_statement):
        self.services.insert(0, f"{import_statement}\n")
        self.services.append(f"        {instance_statement}\n")

    
    def build(self):
      self.write_lines("infra/services/__init__.py", self.services)