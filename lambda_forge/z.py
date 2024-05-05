import json
from lambda_forge.builders.layer_builder import LayerBuilder
from lambda_forge import layers, live_cli
external = "requests"
requirements = "requirements.txt"
layer_builder = LayerBuilder.a_layer().with_layers()

cdk = open("cdk.json", "r").read()
region = json.loads(cdk)["context"].get("region")

    
layer_arn = layers.deploy_external_layer(external, region)
layer_builder.with_external_layers(external, layer_arn)
installed_version = layers.install_external_layer(external)
layers.update_requirements_txt(requirements, f"{external}=={installed_version}")


layer_builder.build()


