import random
import json

# Lista de serviços da AWS
services = ["SQS", "API Gateway", "S3"]

# Cores aleatórias
colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#ff00ff"]

# Função para gerar um item de trigger aleatório
def generate_trigger():
    return {
        "title": random.choice(services),
        "color": random.choice(colors),
        "name": f"Dev-Demo-{random.choice(['HelloWorld', 'DataProcessing', 'EventStream'])}"
    }

# Função para gerar um item de informação aleatório
def generate_info():
    return {
        "title": random.choice(services),
        "color": random.choice(colors),
        "name": f"Dev-Demo-{random.choice(['HelloWorld', 'DataProcessing', 'EventStream'])}",
        "triggers": [
            {
                "title": random.choice(services),
                "color": random.choice(colors),
                "name": f"Dev-Demo-{random.choice(['HelloWorld', 'DataProcessing', 'EventStream'])}",
                "input": '{"name": str, "age": int}',
                "output": '{"name": str, "age": int}',
                "triggers": [
                    generate_trigger() for _ in range(random.randint(1, 3))
                ]
            } for _ in range(random.randint(1, 3))
        ]
    }

# Gerando o array de informações aleatórias
random_info = [generate_info() for _ in range(3)]  # Vamos gerar 3 itens aleatórios

# Convertendo para JSON
json_data = json.dumps(random_info, indent=4)
print(json_data)
